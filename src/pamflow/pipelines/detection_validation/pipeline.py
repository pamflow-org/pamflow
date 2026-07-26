from kedro.pipeline import Pipeline, node

from .nodes import (
    compile_manual_annotations,
    fit_precision_models,
    recommend_thresholds,
)


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
            node(  # Log
                func=fit_precision_models,
                inputs=[
                    "validated_annotations@pandas",
                    "params:detection_validation_parameters",
                    "manual_annotation_summary@pandas",
                ],
                outputs=[
                    "precision_model_fits@pandas",
                    "precision_curves@pandas",
                ],
                name="fit_precision_models_node",
            ),
            node(  # Log
                func=recommend_thresholds,
                inputs=[
                    "precision_model_fits@pandas",
                    "params:detection_validation_parameters.target_precision",
                    "params:detection_validation_parameters.significance_level",
                    "params:detection_validation_parameters.score_transform",
                ],
                outputs="detection_validation_summary@pandas",
                name="recommend_thresholds_node",
            ),
        ]
    )
