from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    find_thresholds
    )





def create_pipeline(**kwargs):
    return Pipeline(
        [
            node( # Log
                func=find_thresholds,
                inputs=['manual_annotations@PartitionedDataset',
                        'params:data_science_parameters.correct_column',
                        'params:data_science_parameters.n_jobs',
                        'params:data_science_parameters.probability'
                        ],
                outputs="species_thresholds@pandas",
                name="find_thresholds_node",
            ),

           
            
        ]
    )
