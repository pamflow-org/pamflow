import os
from maad import sound
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import concurrent.futures



def species_detection_single_file(wav_file_path,
                                  lat,
                                  lon,
                                  mediaID,
                                  deploymentID
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
    # species_detections is a list of dictionaries.
    # One  dictionary for each detection having the following keys:
    # dict_keys(['common_name', 'scientific_name', 'start_time', 'end_time', 'confidence', 'label'])
    species_detections=recording.detections

    # Four keys are added to each dictionary:
    # mediaID, deploymentID, classifiedBy
    species_detections_extra_keys=[ {**detection_dict,**{'mediaID':mediaID,'deploymentID':deploymentID, 'classifiedBy':f'Birdnet {analyzer.version}'}}  
                                   for detection_dict in species_detections
                                  ]
    return species_detections_extra_keys

def trim_audio(start_time, end_time,path_audio,segments_file_name):
    audio_array, sr=sound.load(path_audio)
    trimmed_audio=audio_array[int(start_time*sr):int(end_time*sr)]
    return (segments_file_name[0:-4],(trimmed_audio,sr))




def create_segments_single_species_paralell(df,species,n_jobs):
    if n_jobs == -1:
        n_jobs = int(os.cpu_count()*4/5)
    audio_list=[]
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        
        # Use submit for each task
        futures = [executor.submit(trim_audio_enhanced, 
                                   row['eventStart'],
                                   row['eventEnd'],
                                   row['filePath'],
                                   row['segments_file_name']
                                    
                                    ) 
                    for index, row in df.iterrows()
                    ]

        # Get results when tasks are completed
        audio_list = []
        
        i=0
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                
                audio_list.append(result)
            
            except Exception as e:
                i+=1
                print(f"Error processing the {i}th segment for species {species}: {e}")
    
    return {'_'.join(species.split()):dict(audio_list)}