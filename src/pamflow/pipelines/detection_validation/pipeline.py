from kedro.pipeline import Pipeline, node

from .nodes import compile_manual_annotations


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(  # Log
                func=compile_manual_annotations,
                inputs=[
                    "manual_annotations@PartitionedDataset",
                    "params:detection_validation_parameters.positive_values",
                    "params:detection_validation_parameters.negative_values",
                    "params:detection_validation_parameters.uncertain_values",
                    "params:detection_validation_parameters.uncertain_handling",
                ],
                outputs=[
                    "validated_annotations@pandas",
                    "manual_annotation_summary@pandas",
                ],
                name="compile_manual_annotations_node",
            ),
        ]
    )
