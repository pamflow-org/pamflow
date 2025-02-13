"""Project pipelines."""
from typing import Dict

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from kedro_pamflow.pipelines.preprocess import pipeline as preprocess
from kedro_pamflow.pipelines.graphical_soundscape import pipeline as graphical_soundscape
from kedro_pamflow.pipelines.acoustic_indices import pipeline as acoustic_indices
from kedro_pamflow.pipelines.birdnet import pipeline as birdnet
from kedro_pamflow.pipelines.data_science import pipeline as data_science






def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    preprocess_pipeline = preprocess.create_pipeline()
    graphical_soundscape_pipeline = graphical_soundscape.create_pipeline()
    acoustic_indices_pipeline = acoustic_indices.create_pipeline()
    birdnet_pipeline = birdnet.create_pipeline()
    data_science_pipeline     = data_science.create_pipeline()
    
    
    pamflow_pipeline=preprocess_pipeline + graphical_soundscape_pipeline+acoustic_indices_pipeline+birdnet_pipeline #no incluir data_science

    
    return {
        "__default__":pamflow_pipeline,
        "pamflow": pamflow_pipeline+data_science_pipeline,#+birdnet_pipeline+acousti...,
        "preprocess": preprocess_pipeline,
        "graphical_soundscape":graphical_soundscape_pipeline,
        "acoustic_indices":acoustic_indices_pipeline,
        "birdnet": birdnet_pipeline,
        "data_science": data_science_pipeline,
        
        
    }