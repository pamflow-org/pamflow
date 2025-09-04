import os
import concurrent.futures
import pandas as pd
import itertools as it
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import logging
from pamflow.pipelines.species_detection.utils import (
    species_detection_single_file,
    trim_audio,
)

# Set up logging
logger = logging.getLogger(__name__)

def species_detection_parallel(media, deployments, n_jobs):
    """Detects species in media files using parallel processing.

    This node processes media files and deployment metadata to perform species
    detection in parallel. The inputs correspond to the catalog entries
    `media@pamDP` and `deployments@pamDP`. The output is stored in the catalog
    as `unfiltered_observations@pamDP`.

    Parameters
    ----------
    media : pandas.DataFrame
        A DataFrame containing metadata of media files, following the pamDP.media format.
        Loaded from the catalog entry `media@pamDP`.

    deployments : pandas.DataFrame
        A DataFrame containing deployment metadata, including sensor locations
        (latitude and longitude). Loaded from the catalog entry `deployments@pamDP`.

    n_jobs : int
        The number of parallel jobs to use for species detection. Passed as
        `params:species_detection_parameters.n_jobs`. If set to -1, the number of jobs will
        be equal to the number of CPU cores.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the detected species observations. Stored in the catalog
        as `unfiltered_observations@pamDP`.
        The DataFrame follows the pamDP.observations format.
    """

    deployments = deployments[["deploymentID", "latitude", "longitude"]]

    df = media.merge(deployments, on="deploymentID", how="left")

    if n_jobs == -1:
        n_jobs = os.cpu_count()

    logger.info(
        f"Computing species detection for {df.shape[0]} files using {n_jobs} threads"
    )
    # Use concurrent.futures for parelell execution
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        # Use submit for each task
        futures = [
            executor.submit(
                species_detection_single_file,
                row["filePath"],
                row["latitude"],
                row["longitude"],
                row["mediaID"],
                row["deploymentID"],
            )
            for idx, row in df.iterrows()
        ]

        # Get results when tasks are completed
        results = []

        i = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()

                results.append(result)

            except Exception as e:
                i += 1
                print(f"Error processing the {i}th: files {e}")

    # Build dataframe with results
    resultados_por_carpeta_unchained = list(it.chain.from_iterable(results))
    df_out = pd.DataFrame(resultados_por_carpeta_unchained)
    column_names_dict = {
        "scientific_name": "scientificName",
        "start_time": "eventStart",
        "end_time": "eventEnd",
        "confidence": "classificationProbability",
    }
    #'common_name', 'scientific_name', 'start_time', 'end_time', 'confidence', 'label'
    observations = df_out.rename(columns=column_names_dict)

    observations["observationID"] = observations.index
    observations["classificationTimestamp"] = pd.to_datetime("today")
    observations["observationType"] = "animal"
    observations["classificationMethod"] = "machine"

    observations["eventID"] = None
    observations["observationComments"] = None
    observations["classificationProbability"] = observations["classificationProbability"].astype(float).round(3)
    

    # observations['mediaID']=observations['filePath'].str.split(os.sep).str[-1]
    observations = observations.drop(columns=["common_name", "label"])
    logger.info(
        f"Species detection completed! Detected {observations.shape[0]} observations."
    )
    return observations


def filter_observations(
    observations, target_species, minimum_observations, segment_size
):
    """Filters species observations based on target species and minimum observation criteria.

    This node processes species observations to retain only those that match the target
    species and meet the minimum number of observations required. The inputs correspond
    to the catalog entries `unfiltered_observations@pamDP` and `target_species@pandas`.
    The output is stored in the catalog as `observations@pamDP`.

    Parameters
    ----------
    observations : pandas.DataFrame
        A DataFrame containing unfiltered species observations. Loaded from the catalog
        entry `unfiltered_observations@pamDP`.
        The DataFrame follows the pamDP.observations format.

    target_species : pandas.DataFrame
        A DataFrame containing the list of target species to filter. Loaded from the catalog
        entry `target_species@pandas`.

    minimum_observations : int
        The minimum number of observations required for each species. Passed as
        `params:species_detection_parameters.minimum_observations`.

    segment_size : int
        The number of segments per species. Passed as `params:species_detection_parameters.segment_size`.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the filtered species observations. Stored in the catalog
        as `observations@pamDP`. The DataFrame follows the pamDP.observations format.
    """
    if segment_size > minimum_observations:
        raise ValueError(f"""Number of segments per species ({segment_size}) is greater than minimum number of observations per species ({minimum_observations}).\n 
                             Change the values of these parameters in conf/base/paramteres.yml  to fix this issue. 
        """)

    target_species = target_species.drop_duplicates()
    if target_species.shape[0] != 0:
        observations = observations[
            observations["scientificName"].isin(target_species["scientificName"])
        ]
    else:
        logger.info(
        f"Observations file was not filtered as no target species were provided."
       )
    
    if observations.shape[0] == 0:
        raise ValueError(f"""None of the {target_species.shape[0]} species in data/input/target_species/target_species.csv are among the detected species in 
                            data/output/species_detection/unfiltered_observations.csv. \n
                            This caused the observations file to be empty which is incompatible with the rest of the pipeline \n 
                            Include more or different species in data/input/target_species/target_species.csv to fix this issue.
         """)

    observations = observations[
        observations.groupby("scientificName").transform("size") >= minimum_observations
    ]
    if observations.shape[0] == 0:
        raise ValueError(f"""None of the {target_species.shape[0]} species in data/input/target_species/target_species.csv have as many observations as requested  in params:species_detection_parameters.minimum_observations ({minimum_observations}). \n 
                            This caused the observations file to be empty which is incompatible with the rest of the pipeline \n 
                            Include more or different species in data/input/target_species/target_species.csv or decrease  params:species_detection_parameters.minimum_observations to fix this issue.
         """)
    return observations


def create_segments(observations, media, segment_size):
    """Creates audio segments for species observations.

    This node processes filtered species observations and media metadata to generate
    audio segments for each species (time segments from media files where an animal
    is persumed to be present). The inputs correspond to the catalog entries
    `observations@pamDP` and `media@pamDP`. The output is a DataFrame containing the
    generated segments.

    Parameters
    ----------
    observations : pandas.DataFrame
        A DataFrame containing filtered species observations. Loaded from the catalog
        entry `observations@pamDP`. The DataFrame follows the pamDP.observations format.

    media : pandas.DataFrame
        A DataFrame containing metadata of media files. Loaded from the catalog entry
        `media@pamDP`. The DataFrame follows the pamDP.media format.

    segment_size : int
        The number of segments to sample per species. Passed as
        `params:species_detection_parameters.segment_size`.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the generated audio segments. Each row represents a segment
        with its associated metadata, including file paths and classification probabilities.
        Stored in the catalog as `segments@pandas`.
    """

    # Sample segment_size rows per each species in observations
    observations = observations.merge(
        media[["mediaID", "filePath"]], on="mediaID", how="left"
    )
    segments = (
        observations.groupby(["scientificName"])
        .apply(lambda x: x.sample(int(segment_size)))
        .reset_index(drop=True)
    )

    segments["classificationProbabilityRounded"] = (
        segments["classificationProbability"].round(3).astype(str).str.ljust(5, "0")
    )

    segments["segmentsFilePath"] = segments.apply(
        lambda x: f"{x['classificationProbabilityRounded']}_{x['mediaID'].replace('.WAV', '')}_{x['eventStart']}_{x['eventEnd']}.WAV",
        axis=1,
    )

    return segments


def create_segments_folder(segments, n_jobs, segment_size):
    """Creates audio segment files for species observations.

    This node processes the generated audio segments and creates individual audio (.WAV) files
    for each segment. The input corresponds to the catalog entry `segments@pandas`.
    The output is stored in the catalog as `segments_audio_folder@AudioFolderDataset`
    in separated folder for each species. The file naming format is the following:
    "classificationProbability_mediaID_eventStart_eventEnd.WAV"

    Parameters
    ----------
    segments : pandas.DataFrame
        A DataFrame containing the generated audio segments. Loaded from the catalog
        entry `segments@pandas`.

    n_jobs : int
        The number of parallel jobs to use for creating audio segment files. Passed as
        `params:species_detection_parameters.n_jobs`.

    segment_size : int
        The number of segments to sample per species. Passed as
        `params:species_detection_parameters.segment_size`.

    Yields
    ------
    dict
        A dictionary where the keys are the file paths of the generated audio segment files
        (organized by species) and the values are the corresponding audio data. Stored in
        the catalog as `segments_audio_folder@AudioFolderDataset`.
    """
    logger.info(f'Writing {segments.shape[0]} audio segments to disk...')
    for index, row in segments.iterrows():
        result = trim_audio(
            row["eventStart"],
            row["eventEnd"],
            row["filePath"],
            row["segmentsFilePath"],
        )
        yield {f"{'_'.join(row['scientificName'].split())}/{result[0]}": result[1]}


def create_manual_annotation_formats(segments, manual_annotations_file_name):
    """Creates formats for manual annotation of species observations.

    This node processes the generated audio segments to create manual annotation
    files in a partitioned dataset format. The input corresponds to the catalog
    entry `segments@pandas`. The output is stored in the catalog as
    `manual_annotations@PartitionedDataset`.

    Parameters
    ----------
    segments : pandas.DataFrame
        A DataFrame containing the generated audio segments. Loaded from the catalog
        entry `segments@pandas`.

    manual_annotations_file_name : str
        A generic file name template for the manual annotation files. Passed as
        `params:species_detection_parameters.manual_annotations_file_name`. The file name
        will be customized for each species.

    Returns
    -------
    PartitionedDataset
        A dictionary where the keys are the file names for each species and the values
        are the corresponding DataFrames containing the manual annotation data. Stored
        in the catalog as `manual_annotations@PartitionedDataset`.
    """
    # Dictionary following the format
    # {'Genus_species': 'generic_file_name_for_Genus_species'}
    excel_formats_file_names = {
        "_".join(species.split()): manual_annotations_file_name.replace(
            "species", "_".join(species.split())
        )
        for species in segments["scientificName"].unique()
    }

    excel_generic_format = segments[
        [
            "segmentsFilePath",
            "filePath",
            "classificationProbability",
            "eventStart",
            "eventEnd",
            "scientificName",
        ]
    ].copy()

    excel_generic_format["positive"] = ""

    excel_generic_format["detectedSpecies"] = ""

    manual_annotations_partitioned_dataset = {
        excel_formats_file_names["_".join(species.split())]: excel_generic_format[
            excel_generic_format["scientificName"] == species
        ].sort_values(by="segmentsFilePath", ascending=False)
        for species in segments["scientificName"].unique()
        if "_".join(species.split()) in excel_formats_file_names.keys()
    }
    return manual_annotations_partitioned_dataset

def plot_observations_summary(observations, media):
    """Plots a summary of the observations including number of observations, species, recordings with/without observations, and machine/human observations."""

    #%% Get data from pamDP
    n_observations = len(observations)
    n_observations_time = round((observations.eventEnd - observations.eventStart).sum() / 60,1)
    n_species = observations['scientificName'].nunique()
    n_recordings = len(media)
    n_recordings_with_observations = media["mediaID"].isin(observations["mediaID"]).sum()
    n_recordings_without_observations = n_recordings - n_recordings_with_observations
    percent_recordings_with_observations = round(n_recordings_with_observations/n_recordings * 100,1)
    percent_recordings_without_observations = 100 - percent_recordings_with_observations
    n_machine_observations = (observations.classificationMethod == 'machine').sum()
    n_human_observations = (observations.classificationMethod == 'human').sum()
    percent_machine_observations = round((n_machine_observations / n_observations) * 100,1)
    percent_human_observations = round((n_human_observations / n_observations) * 100,1)

    # Build table data structure
    data = [
        (f"{n_observations} | {n_observations_time} h", "Observations"),
        (n_species, "Species"),
        (f"{percent_recordings_with_observations} %", "Recordings with\nobservations"),
        (f"{percent_recordings_without_observations} %", "Recordings without\nobservations"),
        (f"{percent_machine_observations} %", "Machine observations"),
        (f"{percent_human_observations} %", "Human observations"),
    ]


    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis("off")

    # Grid layout
    cols = 2
    rows = (len(data) + 1) // cols
    card_w, card_h = 0.4, 0.18
    x_margin, y_margin = 0.05, 0.05
    x_spacing, y_spacing = 0.1, 0.1

    for i, (value, label) in enumerate(data):
        row, col = divmod(i, cols)
        x = x_margin + col * (card_w + x_spacing)
        y = 1 - y_margin - (row + 1) * (card_h + y_spacing)
        
        # Draw rounded rectangle
        box = FancyBboxPatch((x, y), card_w, card_h,
                            boxstyle="round,pad=0.02,rounding_size=0.05",
                            linewidth=1, edgecolor="lightgray", facecolor="white")
        ax.add_patch(box)
        
        # Add text
        ax.text(x + card_w/2, y + card_h*0.6, value,
                ha="center", va="center", fontsize=15, weight="bold")
        ax.text(x + card_w/2, y + card_h*0.25, label,
                ha="center", va="center", fontsize=12, color="gray")

    # Add title before plt.show()
    ax.text(0.05, 0.95, "Observations Summary",
            ha="left", va="center",
            fontsize=18, color="gray", weight="bold",
            transform=ax.transAxes)
    
    # Adjust axes
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 1)
    plt.tight_layout()
    
    return fig

def plot_observations_per_species(observations):
    
    species_series = observations['scientificName'].value_counts().head(20)
    species_series.sort_values(ascending=True, inplace=True)
    total_species = len(species_series)

    # if there are more than 20 species, take the top 20
    if total_species > 20:
        top_species = species_series.sort_values(ascending=True).head(20)
        title = f"Number of observations per species | Top 20 of {total_species} species)"
    else:
        top_species = species_series.sort_values(ascending=True)
        title = f"Number of observations per species | {total_species} species"
    
    # Create horizontal bar plot
    fig, ax = plt.subplots(figsize=(8, 6))

    labels = top_species.index
    counts = top_species.values

    ax.barh(labels, counts, alpha=0.85)

    # Add labels
    for i, v in enumerate(counts):
        ax.text(v+2, i, str(v), va='center', ha='left', 
                c='grey')

    # Titles and axes labels
    ax.set_title(title, color="gray", weight="bold", fontsize=14)

    # Clean unneded elements of the plot (axes border, x axis and y ticks)
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.tick_params(axis="y", left=False)

    plt.tight_layout()
    return fig