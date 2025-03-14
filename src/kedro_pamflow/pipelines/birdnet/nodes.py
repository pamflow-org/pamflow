import os
import concurrent.futures
import pandas as pd
import itertools as it
import numpy as np
from kedro_pamflow.pipelines.birdnet.utils import (
    species_detection_single_file,
    trim_audio
    )



def species_detection_parallel(media, 
                               deployments,
                             n_jobs
                            
                             ):
    
    

    deployments=deployments[['deploymentID','latitude','longitude']]



    df=media.merge(deployments,
                on='deploymentID',
                how='left'
                )
    
    
    
    if n_jobs == -1:
        n_jobs = os.cpu_count()

    print(f'Automatic detection of species for {df.shape[0]} files with {n_jobs} threads')
    # Use concurrent.futures for parelell execution
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        
        # Use submit for each task
        futures = [executor.submit(species_detection_single_file, 
                                                                row['filePath'] ,
                                                                row['latitude'] ,
                                                                row['longitude'],
                                                                row['mediaID'],
                                                                row['deploymentID']
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
    column_names_dict={
    'scientific_name':'scientificName',
    'start_time':'bboxTime',
    'end_time':'bboxDuration',
    'confidence':'classificationProbability',
    }
    #'common_name', 'scientific_name', 'start_time', 'end_time', 'confidence', 'label'
    observations=df_out.rename(columns=column_names_dict)

    observations['observationID' ]=observations.index
    observations['classificationTimestamp']=pd.to_datetime('today')
    observations['observationType']='animal'
    observations['classificationMethod']='machine'

    observations['eventID']=None
    observations['observationComments']=None
    observations['bboxFrequency']=None
    observations[ 'bboxBandwidth']=None

    #observations['mediaID']=observations['filePath'].str.split(os.sep).str[-1]
    observations=observations.drop(columns=['common_name','label'])
    return observations

def filter_observations(observations,target_species,minimum_observations, segment_size):
    if segment_size> minimum_observations:
        raise ValueError(f"""Number of segments per species ({segment_size}) is greater than minimum number of observations per species ({minimum_observations}).\n 
                             Change the values of these parameters in conf/base/paramteres.yml  to fix this issue. 
        """)


    target_species=target_species.drop_duplicates()
    observations=observations[observations['scientificName'].isin(target_species['scientificName'])]
    if observations.shape[0]==0:
        raise ValueError(f"""None of the {target_species.shape[0]} species in data/input/target_species/target_species.csv are among the detected species in 
                            data/output/birdnet/unfiltered_observations.csv. \n
                            This caused the observations file to be empty which is incompatible with the rest of the pipeline \n 
                            Include more or different species in data/input/target_species/target_species.csv to fix this issue.
         """)


    observations=observations[observations.groupby('scientificName').transform('size')>=minimum_observations]
    if observations.shape[0]==0:
        raise ValueError(f"""None of the {target_species.shape[0]} species in data/input/target_species/target_species.csv have as many observations as requested  in params:birdnet_parameters.minimum_observations ({minimum_observations}). \n 
                            This caused the observations file to be empty which is incompatible with the rest of the pipeline \n 
                            Include more or different species in data/input/target_species/target_species.csv or decrease  params:birdnet_parameters.minimum_observations to fix this issue.
         """)
    return observations

def create_segments(observations, media,segment_size):
    
    #Sample segment_size rows per each species in observations
    observations=observations.merge(media[['mediaID', 'filePath']],
                                on='mediaID',
                                how='left'
)
    segments=observations.groupby(['scientificName']).apply(lambda x: x.sample(int(segment_size))).reset_index(drop=True)

    segments['classificationProbabilityRounded']=segments['classificationProbability'].round(3).astype(str).str.ljust(5,'0')


    segments['segmentsFilePath']=segments.apply(lambda x: f"{x['classificationProbabilityRounded']}_{x['mediaID'].replace('.WAV','')}_{x['bboxTime']}_{x['bboxDuration']}.WAV" , axis=1)

    return segments

def create_segments_folder(segments,n_jobs,segment_size):
    for index, row in segments.iterrows():
        result=trim_audio(row['bboxTime'],
                            row['bboxDuration'],
                            row['filePath'],
                            row['segmentsFilePath']
                            )
        yield {f"{'_'.join(row['scientificName'].split())}/{result[0]}":result[1]}


def create_manual_annotation_formats(segments,manual_annotations_file_name):
    #Dictionary of the form {'Genus_species': 'generic_file_name_for_Genus_species'}
    excel_formats_file_names={'_'.join(species.split()): manual_annotations_file_name.replace('species','_'.join(species.split()))
                        for species in segments['scientificName'].unique()
                            }

    excel_generic_format=segments[['segmentsFilePath',
                                'filePath',
                               'classificationProbability',
                               'bboxTime', 
                               'bboxDuration',
                               'scientificName', 
        ]]


    excel_generic_format['positive']=''

    excel_generic_format['detectedSpecies']=''

    manual_annotations_partitioned_dataset={excel_formats_file_names['_'.join(species.split())]:
                                            excel_generic_format[excel_generic_format['scientificName']==species
                                            ].sort_values(by='segmentsFilePath',ascending=False)
                                            
                                            for species in segments['scientificName'].unique()
                                            if '_'.join(species.split()) in excel_formats_file_names.keys()
                            }
    return manual_annotations_partitioned_dataset













