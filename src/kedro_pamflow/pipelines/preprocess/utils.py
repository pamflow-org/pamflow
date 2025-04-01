#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""

import os
import argparse
import shutil
import pandas as pd
import numpy as np
import glob
import yaml
from pathlib import Path
from os import listdir
from maad import sound, util
import matplotlib.pyplot as plt

# ----------------------------------
# Main Utilities For Nodes
# ----------------------------------


# --------------------
# Time Lapse Functions
# --------------------
def concat_audio(flist, sample_len=1, verbose=False):
    """Concatenates samples using a list of audio files

    Parameters
    ----------
    flist : list or pandas Series
        List of files to concatenate
    sample_len : float, optional
        Length in seconds of each sample, default is 1 second


    Return
    ------
    long_wav : Numpy array
         All concatenated numpy arrays corresponding to the wav
         files in flist
    fs : float
       Sample frequency of long_wav
    """

    # Compute long wav
    long_wav = list()
    for idx, fname in enumerate(flist, start=1):
        if verbose:
            print(f"{idx} / {len(flist)} : {os.path.basename(fname)}", end="\r")
        s, fs = sound.load(fname)
        s = sound.trim(s, fs, 0, sample_len)
        long_wav.append(s)

    long_wav = np.concatenate(long_wav)

    return long_wav, fs
