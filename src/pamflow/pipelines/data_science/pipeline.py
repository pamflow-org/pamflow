from kedro.pipeline import Pipeline, node, pipeline
from .nodes import find_thresholds, build_train_test_dataset


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(  # Log
                func=find_thresholds,
                inputs=[
                    "manual_annotations@PartitionedDataset",
                    "params:data_science_parameters.correct_column",
                    "params:data_science_parameters.n_jobs",
                    "params:data_science_parameters.probability",
                ],
                outputs="species_thresholds@pandas",
                name="find_thresholds_node",
            ),
            node(
                func=build_train_test_dataset,
                inputs=[
                    "manual_annotations@PartitionedDataset",
                    "params:data_science_plot",
                    "params:data_science_parameters.train_size",
                ],
                outputs=[
                    "train_spectrograms@ImageFolderDataset",
                    "test_spectrograms@ImageFolderDataset",
                ],
                name="build_train_test_dataset_node",
            ),
        ]
    )
