from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    get_media_file,
    get_media_summary,
    field_deployments_sheet_to_deployments,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(  # Log
                func=get_media_file,
                inputs=["params:audio_root_directory"],
                outputs="media@pamDP",
                name="get_media_file_node",
            ),
            node(  # Log
                func=get_media_summary,
                inputs=["media@pamDP"],
                outputs="media_summary@pandas",
                name="get_media_summary_node",
            ),
            
            node(  # Log
                func=field_deployments_sheet_to_deployments,
                inputs=["field_deployments_sheet@pandas", "media_summary@pandas"],
                outputs="deployments@pamDP",
                name="field_deployments_sheet_to_deployments_node",
            ),
            
        ]
    )
