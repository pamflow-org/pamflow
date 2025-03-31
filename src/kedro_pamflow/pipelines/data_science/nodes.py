import os
import pandas as pd
import concurrent.futures
from kedro_pamflow.pipelines.data_science.utils import (
    find_threshold_single_species,
    spectrograms_single_species,
)
import random


def find_thresholds(manual_annotations, correct, n_jobs, probability):
    """Calculates probability thresholds for each species based on manual annotations.

    This node processes manual annotations to calculate an optimal probability threshold 
    for each species. The input corresponds to the catalog entry 
    `manual_annotations@PartitionedDataset`. The output is stored in the catalog as 
    `species_thresholds@pandas`.

    Parameters
    ----------
    manual_annotations : dict
        A dictionary where the keys are species names and the values are functions that 
        return DataFrames with manual annotations for each species. Loaded from the catalog 
        entry `manual_annotations@PartitionedDataset`.

    correct : float
        The minimum percentage of correct observations required to calculate the threshold.

    n_jobs : int
        The number of parallel jobs to use for processing. If set to -1, 80% of the available 
        CPU cores will be used. Passed as `params:data_science_parameters.n_jobs`.

    probability : float
        The initial probability value used to calculate thresholds. Passed as 
        `params:data_science_parameters.probability`.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the calculated probability thresholds for each species. 
        Stored in the catalog as `species_thresholds@pandas`. The DataFrame includes two 
        columns: `species` (the species name) and `threshold` (the calculated probability 
        threshold).
    """
    data_list = [dataframe() for species, dataframe in manual_annotations.items()]

    if n_jobs == -1:
        n_jobs = int(os.cpu_count() * 4 / 5)

    print(
        f"""Calculating species thresholds for {len(manual_annotations.keys())} species"""
    )

    with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        results = executor.map(
            find_threshold_single_species,
            [
                (
                    data,
                    correct,
                    data["scientific_name"].unique().tolist()[0],
                    probability,
                )
                for data in data_list
            ],
        )

        # Get results when tasks are completed
        thresholds_dataframe_list = []

        i = 0
        for result in results:
            try:
                # result = future.result()
                # print(species)
                thresholds_dataframe_list.append(result)

            except Exception as e:
                i += 1
                print(f"Error processing the {i}th species: files {e}")

    thresholds_dataframe = pd.DataFrame(thresholds_dataframe_list)
    return thresholds_dataframe[["species", "threshold"]]


def build_train_test_dataset(manual_annotations, plot_params, train_size):
    all_manual_annotations = pd.concat(
        [manual_annotations[species]() for species in manual_annotations.keys()]
    )
    all_manual_annotations = all_manual_annotations[all_manual_annotations["positive"]]
    train = []
    test = []
    for species in all_manual_annotations["scientific_name"].unique():
        file_names_list = all_manual_annotations[
            all_manual_annotations["scientific_name"] == species
        ]["segments_file_name"].tolist()
        species_spectrograms_list = spectrograms_single_species(
            species, file_names_list, plot_params
        )

        random.shuffle(species_spectrograms_list)
        species_train = species_spectrograms_list[
            : int(train_size * len(species_spectrograms_list))
        ]
        species_test = species_spectrograms_list[
            int(train_size * len(species_spectrograms_list)) :
        ]

        train += species_train
        test += species_test
    train_spectrograms = {
        main_tup[0]: dict(tup[1:] for tup in train if tup[0] == main_tup[0])
        for main_tup in train
    }
    test_spectrograms = {
        main_tup[0]: dict(tup[1:] for tup in test if tup[0] == main_tup[0])
        for main_tup in test
    }
    return train_spectrograms, test_spectrograms
