#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""

import time
import logging
from pamflow.pipelines.acoustic_indices.utils import compute_indices_parallel
logger = logging.getLogger(__name__)

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
    params_preprocess = acoustic_indices_parameters["preprocess"]
    params_indices = acoustic_indices_parameters["indices_settings"]
    n_jobs = acoustic_indices_parameters["execution"]["n_jobs"]
    media = media[media["fileLength"] > 0]
    
    groups = media["deploymentID"].nunique()
    logger.info(f"Computing acoustic indices for {groups} ({media.shape[0]} files)")

    for deployment, media_gp in media.groupby('deploymentID'):
        logger.info(f"Computing acoustic indices for {deployment} ({media_gp.shape[0]} files)")
        acoustic_indices = compute_indices_parallel(
            media_gp, params_preprocess, params_indices, n_jobs)
    
        yield {f'indices_{deployment}': acoustic_indices}
