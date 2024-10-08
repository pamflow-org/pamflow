#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import glm

# ----------------------------------
# Main Utilities For Other Functions
# ----------------------------------
#%% Load configuration file
def find_threshold_single_species(params_tuple):
    data,correct,species,probability=params_tuple
    """Fit null and confidence models, and return both models."""
    null_model = glm(f'{correct} ~ 1', data=data, family=sm.families.Binomial()).fit()
    conf_model = glm(f'{correct} ~ confidence', data=data, family=sm.families.Binomial()).fit()

    logit_value = np.log(probability / (1 - probability))
    cutoff = (logit_value - conf_model.params['Intercept']) / conf_model.params['confidence']
    return {'threshold':cutoff,'species':species}