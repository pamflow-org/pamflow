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


def util_function(flist, sample_len=1, verbose=False):
    return 2 + 2
