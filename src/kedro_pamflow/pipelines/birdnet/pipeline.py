from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    species_detection_parallel,
    filter_detections,
    create_segments,
    create_segments_folder,
    create_manual_annotation_formats,
    create_segments_folder
    )







def create_pipeline(**kwargs):
    return Pipeline(
        [
            node( # Log
                func=species_detection_parallel,
                inputs=[ "media@pandas",'deployment@pandas','params:birdnet_parameters.n_jobs','params:deployment_parameters'],
                outputs="unfiltered_observation@pandas",
                name="species_detection_node",
            ),
            node( # Log
                func=filter_detections,
                inputs=[ 'unfiltered_observation@pandas','especies_de_interes@pandas','params:birdnet_parameters.minimum_observations'],
                outputs="observation@pandas",
                name="filter_detections_node",
            ),
             node( # Log
                func=create_segments,
                inputs=[ 'observation@pandas','params:birdnet_parameters.segment_size'],
                outputs="segments@pandas",
                name="create_segments_node",
            ),
            node( # Log
                func=create_segments_folder,
                inputs=[ "segments@pandas",'params:birdnet_parameters.n_jobs','params:birdnet_parameters.segment_size'],
                outputs="segments_audio_folder@AudioFolderDataset",
                name="create_segments_folder_node",
            ),
            node( # Log
                func=create_manual_annotation_formats,
                inputs=[ 'segments@pandas','params:birdnet_parameters.manual_annotations_file_name'],
                outputs="manual_annotations@PartitionedDataset",
                name="create_manual_annotation_formats_node",
            )
         
        ]
    )
