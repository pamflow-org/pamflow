"""
This is a boilerplate pipeline 'filter_media'
generated using Kedro 0.19.8
"""


from kedro.pipeline import Pipeline, node, pipeline
from .nodes import filter_media

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=filter_media,
            inputs=["media@pamDP", "params:deployments_filter"],
            outputs="media_work",
            name="filter_media_node",
        )
    ])

def with_filter_media(downstream: Pipeline) -> Pipeline:
    """Prepend the media filter node to any pipeline."""
    return create_pipeline() + downstream