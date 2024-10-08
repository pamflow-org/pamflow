#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The functions here are a variant of the original graphical soundscapes introduced by Campos-Cerqueira et al. The peaks are detected on the spectrogram instead of detecting peaks on the spectrum. Results are similar but not equal to the ones computed using seewave in R.

References:
  - Campos‐Cerqueira, M., et al., 2020. How does FSC forest certification affect the acoustically active fauna in Madre de Dios, Peru? Remote Sensing in Ecology and Conservation 6, 274–285. https://doi.org/10.1002/rse2.120
  - Furumo, P.R., Aide, T.M., 2019. Using soundscapes to assess biodiversity in Neotropical oil palm landscapes. Landscape Ecology 34, 911–923.
  - Campos-Cerqueira, M., Aide, T.M., 2017. Changes in the acoustic structure and composition along a tropical elevational gradient. JEA 1, 1–1. https://doi.org/10.22261/JEA.PNCO7I
"""
import os
import argparse
import pandas as pd
import glob
import matplotlib.pyplot as plt
from maad import sound, util
from maad.rois import spectrogram_local_max
from maad.features import graphical_soundscape as graphical_soundscape_maad


def graphical_soundscape_pamflow(df,graphical_soundscape_parameters):
#elif args.operation == "graphical_soundscape":
    df['date'] = pd.to_datetime(df.date)
    df['time'] = df.date.dt.hour
    
    # If file list provided filter dataframe
    #if select_sites is None:
    #    n_sites = df.groupby('sensor_name').ngroups
    #    site_list = df.sensor_name.unique()
    #else:
    #    df = df[df['sensor_name'].isin(select_sites)]
    #    n_sites = df.groupby('sensor_name').ngroups
    #    site_list = df.sensor_name.unique()
    #print(f'Computing graph over {n_sites} sites: {site_list}')

    # Group by site
    #if group_by_site:  # saves results per site
    #    for site, df_site in df.groupby('sensor_name'):
    #        df_out = graphical_soundscape(
    #            df_site, threshold_abs, 'path_audio', 'time', target_fs, nperseg, 
    #            noverlap, db_range, min_distance, n_jobs)
    #        fname_save = os.path.join(args.output, f'{site}_graph.csv')
    #        df_out.to_csv(fname_save)
    #        print(f'{site} Done! Results are stored at {fname_save}')
    
    # Compute over all files
    #else:
    threshold_abs=graphical_soundscape_parameters['threshold_abs']
    target_fs=graphical_soundscape_parameters['target_fs']
    nperseg=graphical_soundscape_parameters['nperseg']
    noverlap=graphical_soundscape_parameters['noverlap']
    db_range =graphical_soundscape_parameters['db_range']
    min_distance=graphical_soundscape_parameters['min_distance']
    n_jobs=graphical_soundscape_parameters['n_jobs']

    df_out = graphical_soundscape_maad(
        df[df['length']>0], threshold_abs, 'path_audio', 'time', target_fs, nperseg, 
        noverlap, db_range, min_distance, n_jobs)
    return df_out #df_out.to_csv(args.output, index=False)

