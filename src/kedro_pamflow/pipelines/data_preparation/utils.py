#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""

import os
import numpy as np
from maad import sound

# ----------------------------------
# Main Utilities For Nodes
# ----------------------------------

def concat_audio(flist, sample_len=1, verbose=False):
    """Concatenates audio samples using a list of audio files for mixing timelapses

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

    long_wav = list()
    for idx, fname in enumerate(flist, start=1):
        if verbose:
            print(f"{idx} / {len(flist)} : {os.path.basename(fname)}", end="\r")
        s, fs = sound.load(fname)
        s = sound.trim(s, fs, 0, sample_len)
        long_wav.append(s)

    long_wav = np.concatenate(long_wav)

    return long_wav, fs
