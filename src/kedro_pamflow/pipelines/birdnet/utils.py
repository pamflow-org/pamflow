import os
import concurrent.futures
import matplotlib.pyplot as plt
import pandas as pd
from maad import sound, features, util
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import itertools as it
import numpy as np


def species_detection_single_file(wav_file_path,
                                  lat,
                                  lon,
                                  sensor_name
                                 ):
    # Load and initialize the BirdNET-Analyzer models.
    analyzer = Analyzer()
    recording=Recording(
        analyzer,
        wav_file_path,
        lat=lat,
        lon=lon,
        
    )
    recording.analyze()
    species_detections=recording.detections 
    species_detections_extra_keys=[ {**detection_dict,**{'path_audio':wav_file_path,'sensor_name':sensor_name}}  
                                   for detection_dict in species_detections
                                  ]
    return species_detections_extra_keys

def trim_audio(audio_array, 
               sr,
               start_time, 
               end_time):
    
    trimmed_audio=audio_array[int(start_time*sr):int(end_time*sr)]
    return trimmed_audio, sr


def create_segments_single_species(df):
    audio_list=[]
    for index, row in df.iterrows():
        
        start_time        = row['start_time']
        end_time          = row['end_time']
        path_audio        = row['path_audio']
        
        segments_file_name= row['segments_file_name']
        
    
    
        audio_array, sr=sound.load(path_audio)
    
        trimmed_audio, sr=trim_audio(audio_array, 
                    sr,
                    start_time, 
                    end_time)

        

        
        audio_list.append((segments_file_name,(trimmed_audio,sr)))
    return dict(audio_list)