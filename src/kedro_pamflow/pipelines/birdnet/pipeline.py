from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    species_detection_parallel,
    filter_observations,
    create_segments,
    create_segments_folder,
    create_manual_annotation_formats,
    create_segments_folder,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(  # Log
                func=species_detection_parallel,
                inputs=[
                    "media@pamDP",
                    "deployments@pamDP",
                    "params:birdnet_parameters.n_jobs",
                ],
                outputs="unfiltered_observations@pamDP",
                name="species_detection_node",
            ),
            node(  # Log
                func=filter_observations,
                inputs=[
                    "unfiltered_observations@pamDP",
                    "target_species@pandas",
                    "params:birdnet_parameters.minimum_observations",
                    "params:birdnet_parameters.segment_size",
                ],
                outputs="observations@pamDP",
                name="filter_observations_node",
            ),
            node(  # Log
                func=create_segments,
                inputs=[
                    "observations@pamDP",
                    "media@pamDP",
                    "params:birdnet_parameters.segment_size",
                ],
                outputs="segments@pandas",
                name="create_segments_node",
            ),
            node(  # Log
                func=create_segments_folder,
                inputs=[
                    "segments@pandas",
                    "params:birdnet_parameters.n_jobs",
                    "params:birdnet_parameters.segment_size",
                ],
                outputs="segments_audio_folder@AudioFolderDataset",
                name="create_segments_folder_node",
            ),
            node(  # Log
                func=create_manual_annotation_formats,
                inputs=[
                    "segments@pandas",
                    "params:birdnet_parameters.manual_annotations_file_name",
                ],
                outputs="manual_annotations@PartitionedDataset",
                name="create_manual_annotation_formats_node",
            ),
        ]
    )
