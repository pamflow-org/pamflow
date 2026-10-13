#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""

import os
import numpy as np
import pandas as pd
from matplotlib.text import Text
from matplotlib.transforms import Bbox
from maad import sound

VARIABLES = {
    "fileLength": "Duration (s)",
    "sampleRate": "Sample rate (Hz)",
}
OUTLIER_COLOR = "#D55E00"
NORMAL_COLOR = "#0072B2"

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


def flag_outliers(df, z_threshold=3.5):
    """Flag outliers in fileLength and sampleRate per deployment.

    Uses a robust z-score, 0.6745 * (x - median) / MAD. If MAD is 0
    (homogeneous deployment), any value different from the median is flagged.

    Parameters
    ----------
    df : pandas DataFrame
        Media table with columns deploymentID, fileLength and sampleRate.
    z_threshold : float, optional
        Absolute robust z-score above which a value is an outlier.

    Return
    ------
    df : pandas DataFrame
        Copy of df with columns out_<var> and z_<var> for each variable,
        and is_outlier (True if any variable is an outlier).
    """
    df = df.copy()
    for col in VARIABLES:
        flag = pd.Series(False, index=df.index)
        z_all = pd.Series(0.0, index=df.index)
        for _, grp in df.groupby("deploymentID"):
            med = grp[col].median()
            mad = (grp[col] - med).abs().median()
            if mad == 0:
                is_out = ~np.isclose(grp[col], med)
                z = pd.Series(np.where(is_out, np.inf, 0.0), index=grp.index)
            else:
                z = 0.6745 * (grp[col] - med) / mad
                is_out = z.abs() > z_threshold
            flag.loc[grp.index] = is_out
            z_all.loc[grp.index] = z
        df[f"out_{col}"] = flag
        df[f"z_{col}"] = z_all
    df["is_outlier"] = df[[f"out_{c}" for c in VARIABLES]].any(axis=1)
    return df


def deployment_medians(df):
    """Median of each variable in VARIABLES per deployment."""
    return df.groupby("deploymentID")[list(VARIABLES)].median()


def place_labels(fig, ax, points):
    """Label each (x, y, text) point with the first non-overlapping position.

    Candidate positions are tried in order; a position is rejected if its text
    box overlaps another label, any outlier marker, or leaves the axes.
    """
    renderer = fig.canvas.get_renderer()
    axbox = ax.get_window_extent(renderer)
    markers = []
    for px, py, _ in points:
        cx, cy = ax.transData.transform((px, py))
        markers.append(Bbox.from_extents(cx - 9, cy - 9, cx + 9, cy + 9))
    candidates = [(dx, dy, ha) for dy in (7, -13, 21, -27, 35, -41)
                  for dx, ha in ((7, "left"), (-7, "right"))]
    placed = []
    for px, py, text in sorted(points, key=lambda p: p[0]):
        for k, (dx, dy, ha) in enumerate(candidates):
            ann = ax.annotate(
                text, (px, py), xytext=(dx, dy), textcoords="offset points",
                fontsize=7, ha=ha, color=OUTLIER_COLOR,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=OUTLIER_COLOR))
            ann.update_positions(renderer)
            box = Text.get_window_extent(ann, renderer)
            fits = (axbox.x0 <= box.x0 and box.x1 <= axbox.x1
                    and axbox.y0 <= box.y0 and box.y1 <= axbox.y1)
            free = not any(box.overlaps(o) for o in placed + markers)
            if (fits and free) or k == len(candidates) - 1:
                placed.append(box)
                break
            ann.remove()
