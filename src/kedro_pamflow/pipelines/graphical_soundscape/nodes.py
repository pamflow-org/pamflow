#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The functions here are a variant of the original graphical soundscapes introduced by Campos-Cerqueira et al. The peaks are detected on the spectrogram instead of detecting peaks on the spectrum. Results are similar but not equal to the ones computed using seewave in R.

References:
  - Campos‐Cerqueira, M., et al., 2020. How does FSC forest certification affect the acoustically active fauna in Madre de Dios, Peru? Remote Sensing in Ecology and Conservation 6, 274–285. https://doi.org/10.1002/rse2.120
  - Furumo, P.R., Aide, T.M., 2019. Using soundscapes to assess biodiversity in Neotropical oil palm landscapes. Landscape Ecology 34, 911–923.
  - Campos-Cerqueira, M., Aide, T.M., 2017. Changes in the acoustic structure and composition along a tropical elevational gradient. JEA 1, 1–1. https://doi.org/10.22261/JEA.PNCO7I
"""

import pandas as pd
from maad.features import graphical_soundscape as graphical_soundscape_maad
from maad.features import plot_graph
import matplotlib.pyplot as plt
import logging

# Set up logging
logger = logging.getLogger(__name__)

def graphical_soundscape_pamflow(media, graphical_soundscape_parameters):
    """Generates graphical soundscapes based on spectrogram peaks for acoustic analysis.

    This node processes media files to compute graphical soundscapes using spectrogram
    peaks. The input corresponds to the catalog entry `media@pamDP`, and the parameters
    are passed as `params:graphical_soundscape_parameters`. The output is stored in the
    catalog as `graphical_soundscape@pandas`.

    Parameters
    ----------
    media : pandas.DataFrame
        A DataFrame containing metadata of media files, following the pamDP.media format.
        Loaded from the catalog entry `media@pamDP`.

    graphical_soundscape_parameters : dict
        A dictionary containing parameters for generating graphical soundscapes, such as
        `threshold_abs`, `target_fs`, `nperseg`, `noverlap`, `db_range`, `min_distance`,
        and `n_jobs`. Passed as `params:graphical_soundscape_parameters`.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the computed graphical soundscape data. Stored in the catalog
        as `graphical_soundscape@pandas`.
    """
    # Extract parameters from the input dictionary
    threshold_abs = graphical_soundscape_parameters["threshold_abs"]
    target_fs = graphical_soundscape_parameters["target_fs"]
    nperseg = graphical_soundscape_parameters["nperseg"]
    noverlap = graphical_soundscape_parameters["noverlap"]
    db_range = graphical_soundscape_parameters["db_range"]
    min_distance = graphical_soundscape_parameters["min_distance"]
    n_jobs = graphical_soundscape_parameters["n_jobs"]
    media["date"] = pd.to_datetime(media.timestamp)
    media["time"] = media.date.dt.hour
    media = media[media["fileLength"] > 0]

    # Compute graphical soundscapes by deploymentID
    for deployment, media_gp in media.groupby('deploymentID'):
        logger.info(f"Computing graphical soundscapes for {deployment} ({media_gp.shape[0]} files)")
        
        # Compute graphical soundscape
        df_out = graphical_soundscape_maad(
            media_gp,  # A Pandas DataFrame containing information about the audio files.
            threshold_abs,
            "filePath",  # Column name where the full path of audio is provided.
            "time",  # Column name where the time is provided as a string using the format ‘HHMMSS’.
            target_fs,
            nperseg,
            noverlap,
            db_range,
            min_distance,
            n_jobs,
        )
        
        # Plot graphical soundscape
        fig, ax = plt.subplots()
        plot_graph(df_out, savefig=False, ax=ax)

        # Save graph and figure as Partitioned Dataset
        yield {f'graph_{deployment}': df_out},  {f'graph_{deployment}': fig}
