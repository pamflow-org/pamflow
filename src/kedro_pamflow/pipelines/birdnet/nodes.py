import os
import concurrent.futures
import pandas as pd
import itertools as it
import numpy as np
from kedro_pamflow.pipelines.birdnet.utils import (
    species_detection_single_file,
    trim_audio,
    create_segments_single_species_paralell
    )



def species_detection_parallel(metadata, 
                               formato_de_migracion,
                             n_jobs,
                             formato_migracion_parameters
                            
                             ):
    
    device_id=formato_migracion_parameters['device_id']
    latitude_col=formato_migracion_parameters['latitude_col']
    longitude_col=formato_migracion_parameters['longitude_col']

    formato_de_migracion=formato_de_migracion[[device_id,latitude_col,longitude_col]]

    formato_de_migracion=formato_de_migracion.rename(columns={device_id:'sensor_name',
                                                            latitude_col:  "latitud" ,
                                                            longitude_col: "longitud"
                                                            }
                                                    )

    formato_de_migracion["latitud" ]=formato_de_migracion["latitud" ].str.replace(',','.').astype('float64')
    formato_de_migracion["longitud"]=formato_de_migracion["longitud"].str.replace(',','.').astype('float64')


    df=metadata.merge(formato_de_migracion,
                on='sensor_name',
                how='left'
                )
    
    
    
    if n_jobs == -1:
        n_jobs = os.cpu_count()

    print(f'Automatic detection of species for {df.shape[0]} files with {n_jobs} threads')
    
    # Use concurrent.futures for parelell execution
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        
        # Use submit for each task
        futures = [executor.submit(species_detection_single_file, 
                                                                row['path_audio'] ,
                                                                row['latitud'] ,
                                                                row['longitud'],
                                                                row['sensor_name']
                                                            ) 
                    for idx,row in df.iterrows()
                  ]

        # Get results when tasks are completed
        results = []
        
        i=0
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
               
                results.append(result)
            
            except Exception as e:
                i+=1
                print(f"Error processing the {i}th: files {e}")

    # Build dataframe with results
    resultados_por_carpeta_unchained=list(it.chain.from_iterable(results))
    df_out=pd.DataFrame(resultados_por_carpeta_unchained)
    return df_out

def filter_detections(detected_species,especies_de_interes,minimum_observations):
    especies_de_interes=especies_de_interes.drop_duplicates()
    detected_species_filtered=detected_species[detected_species['scientific_name'].isin(especies_de_interes['scientific_name'])]


    detected_species_filtered=detected_species_filtered[detected_species_filtered.groupby('scientific_name').transform('size')>=minimum_observations]
    return detected_species_filtered

def create_segments(detected_species,segment_size):
    num_intervals=max(i for i in range(1, int(segment_size**(1/2))+1)  
                    if segment_size % i == 0
                    )

    samples_per_interval=segment_size/num_intervals

    detected_species['discrete_confidence']=detected_species.groupby(['scientific_name'])['confidence'].transform(
                        lambda x: pd.qcut(x, num_intervals, labels=range(1,num_intervals+1)))

    segments=detected_species.groupby(['scientific_name','discrete_confidence']).apply(lambda x: x.sample(int(samples_per_interval))).reset_index(drop=True)

    segments['original_file_name']=segments['path_audio'].apply(os.path.normpath).str.split(os.sep).str[-1]

    segments['segments_file_name']=segments.apply(lambda x: f"{x['confidence']:.3}_{x['original_file_name']}_{x['start_time']}_{x['end_time']}.WAV" , axis=1)

    return segments

def create_segments_folder(df_segments,n_jobs,segment_size):

    #df_segments['ngroup']=df_segments.groupby('scientific_name').ngroup()

    #df_segments['ngroup']=df_segments.groupby('scientific_name')['ngroup'].transform(np.random.permutation)

    #df_segments=df_segments[df_segments['ngroup']<=19]
    
    results = [create_segments_single_species_paralell(
                                df_segments[df_segments['scientific_name']==species] ,
                                species,
                                n_jobs
                                ) 
                for species in df_segments['scientific_name'].unique()
                ]

    
    
    
    # Build audio_folder_dataset with results
    audio_folder_dataset={ k:v  for diccionario in results for k,v in diccionario.items() }
    

    return audio_folder_dataset


def create_manual_annotation_formats(segments,segments_audio_folder,manual_annotations_file_name):
    excel_formats_file_names={'_'.join(species.split()): manual_annotations_file_name.replace('species','_'.join(species.split()))
                        for species in segments_audio_folder.keys()
                            }

    excel_generic_format=segments[['segments_file_name',
                               'confidence',
                               'original_file_name', 
                               'start_time', 
                               'end_time',
                               'scientific_name', 
        ]]


    excel_generic_format['positive']=np.random.choice([False,True],
                                                    excel_generic_format.shape[0],
                                                    replace=True
                                                    )

    excel_generic_format['detected_species']=np.where(excel_generic_format['positive'],
                                                    excel_generic_format['scientific_name'],
                                                    'other'
                                                    )

    manual_annotations_partitioned_dataset={excel_formats_file_names['_'.join(species.split())]:
                                            excel_generic_format[excel_generic_format['scientific_name']==species
                                            ].sort_values(by='segments_file_name',ascending=False)
                                            
                                            for species in segments['scientific_name'].unique()
                                            if '_'.join(species.split()) in excel_formats_file_names.keys()
                            }
    return manual_annotations_partitioned_dataset













