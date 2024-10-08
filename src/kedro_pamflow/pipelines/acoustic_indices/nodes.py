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

def compute_indices(data, acoustic_indices_parameters):
    target_fs=acoustic_indices_parameters['target_fs']
    filter_type=acoustic_indices_parameters['filter_type']
    filter_cut=acoustic_indices_parameters['filter_cut']
    filter_order=acoustic_indices_parameters['filter_order']
    n_jobs=acoustic_indices_parameters['n_jobs']

    data=data[data['length']>0]    
    df_out = compute_indices_parallel(
            data, target_fs, filter_type, filter_cut, filter_order, n_jobs)
    return df_out

    

