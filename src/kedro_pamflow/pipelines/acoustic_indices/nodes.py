#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""
import os
import argparse
import matplotlib.pyplot as plt
from maad import sound, util
import pandas as pd
import seaborn as sns
from kedro_pamflow.pipelines.acoustic_indices.utils import (
    compute_indices_parallel
    )

def compute_indices(media, acoustic_indices_parameters):
    """Computes acoustic indices for media files.

    This node processes media files to calculate various acoustic indices for 
    ecological analysis. The input corresponds to the catalog entry `media@pamDP`, 
    and the parameters are passed as `params:acoustic_indices_parameters`. The output 
    is stored in the catalog as `acoustic_indices@pandas`.

    Parameters
    ----------
    media : pandas.DataFrame
        A DataFrame containing metadata of media files, following the pamDP.media format. 
        Loaded from the catalog entry `media@pamDP`.

    acoustic_indices_parameters : dict
        A dictionary containing parameters for computing acoustic indices, such as 
        `target_fs`, `filter_type`, `filter_cut`, `filter_order`, and `n_jobs`. Passed 
        as `params:acoustic_indices_parameters`.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the computed acoustic indices. Stored in the catalog 
        as `acoustic_indices@pandas`.
    """
    target_fs=acoustic_indices_parameters['target_fs']
    filter_type=acoustic_indices_parameters['filter_type']
    filter_cut=acoustic_indices_parameters['filter_cut']
    filter_order=acoustic_indices_parameters['filter_order']
    n_jobs=acoustic_indices_parameters['n_jobs']

    media=media[media['fileLength']>0]    
    acoustic_indices = compute_indices_parallel(
            media, target_fs, filter_type, filter_cut, filter_order, n_jobs)
    return acoustic_indices

    

