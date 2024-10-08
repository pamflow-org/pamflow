from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    compute_indices
    )





def create_pipeline(**kwargs):
    return Pipeline(
        [
            node( # Log
                func=compute_indices,
                inputs=['audio_metadata@pandas' ,'params:acoustic_indices'],
                outputs="acoustic_indices@pandas",
                name="compute_indices_node",
            )
            
        ]
    )
