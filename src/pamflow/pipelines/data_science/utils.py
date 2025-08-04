#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""

import numpy as np
import pandas as pd
import os
import statsmodels.api as sm
from statsmodels.formula.api import glm
import concurrent.futures
from maad import sound, util
import matplotlib.pyplot as plt


# ----------------------------------
# Main Utilities For Other Functions
# ----------------------------------
# %% Load configuration file
def find_threshold_single_species(params_tuple):
    data, correct, species, probability = params_tuple
    """Fit null and confidence models, and return both models."""
    null_model = glm(f"{correct} ~ 1", data=data, family=sm.families.Binomial()).fit()
    conf_model = glm(
        f"{correct} ~ confidence", data=data, family=sm.families.Binomial()
    ).fit()

    logit_value = np.log(probability / (1 - probability))
    cutoff = (logit_value - conf_model.params["Intercept"]) / conf_model.params[
        "confidence"
    ]
    return {"threshold": cutoff, "species": species}


def single_spectrogram(species, segments_file_name, plot_params):
    segments_path = "/home/s0nabio/kedroPamflow/data/output/species_detection/segments"
    segments_file_name = os.path.join(
        segments_path, "_".join(species.split()), segments_file_name
    )
    s, fs = sound.load(segments_file_name)

    nperseg = plot_params["nperseg"]
    noverlap = plot_params["noverlap"]
    db_range = plot_params["db_range"]
    width = plot_params["fig_width"]
    height = plot_params["fig_height"]

    fig, ax = plt.subplots(figsize=(width, height))
    Sxx, tn, fn, ext = sound.spectrogram(
        s,
        fs,
        nperseg=nperseg,
        noverlap=0,  # noverlap#nperseg*noverlap
    )
    util.plot_spectrogram(Sxx, ext, db_range, ax=ax, colorbar=False)
    return (species, segments_file_name.replace(".WAV", ""), fig)


def spectrograms_single_species(species, file_names_list, plot_params):
    n_jobs = int(os.cpu_count() * 4 / 5)
    spectrogram_list = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        # Use submit for each task
        futures = [
            executor.submit(single_spectrogram, species, segment_file_name, plot_params)
            for segment_file_name in file_names_list
        ]

        # Get results when tasks are completed

        i = 0

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()

                spectrogram_list.append(result)

            except Exception as e:
                print(
                    f"Error processing the {i}th spectrogram for species {species}: {e}"
                )
            i += 1

    return spectrogram_list
