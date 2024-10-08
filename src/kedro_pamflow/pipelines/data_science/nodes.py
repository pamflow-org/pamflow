#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""
import os
import pandas as pd
import concurrent.futures
from kedro_pamflow.pipelines.data_science.utils import (
    find_threshold_single_species
    )

def find_thresholds(manual_annotations,correct,n_jobs,probability):
    data_list=[ dataframe() for species, dataframe in manual_annotations.items()]

    if n_jobs == -1:
        n_jobs = int(os.cpu_count()*4/5)

    print(f"""Calculating species thresholds for {len(manual_annotations.keys())} species""")

    with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        
        
        results = executor.map(find_threshold_single_species,
                                    [(data,
                                    correct,
                                    data['scientific_name'].unique().tolist()[0],
                                    probability
                                    )
                                     for data in data_list
                                    ]
                                   )
                                                     
        # Get results when tasks are completed
        thresholds_dataframe_list = []
        
        i=0
        for result in results:
            try:
                #result = future.result()
                #print(species)
                thresholds_dataframe_list.append(result)
            
            except Exception as e:
                i+=1
                print(f"Error processing the {i}th species: files {e}")

    thresholds_dataframe=pd.DataFrame(thresholds_dataframe_list)
    return thresholds_dataframe[['species','threshold']]
