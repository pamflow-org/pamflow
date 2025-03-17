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


def graphical_soundscape_pamflow(media,graphical_soundscape_parameters):
  media['date'] = pd.to_datetime(media.timestamp)
  media['time'] = media.date.dt.hour

  threshold_abs=graphical_soundscape_parameters['threshold_abs']
  target_fs=graphical_soundscape_parameters['target_fs']
  nperseg=graphical_soundscape_parameters['nperseg']
  noverlap=graphical_soundscape_parameters['noverlap']
  db_range =graphical_soundscape_parameters['db_range']
  min_distance=graphical_soundscape_parameters['min_distance']
  n_jobs=graphical_soundscape_parameters['n_jobs']

  df_out = graphical_soundscape_maad(
      media[media['fileLength']>0], #A Pandas DataFrame containing information about the audio files.
      threshold_abs, 
    'filePath', #Column name where the full path of audio is provided.
      'time', #Column name where the time is provided as a string using the format ‘HHMMSS’.
      target_fs, 
      nperseg, 
      noverlap, 
      db_range, 
      min_distance, 
      n_jobs
      )
  return df_out 

