from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (from_media_to_media_gbif,
                    from_deployments_to_deployments_gbif,
                    from_observations_to_observations_gbif,
                    from_deployments_to_CSA_eventos,
                    )


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(  
                func=from_media_to_media_gbif,
                inputs=["media@pamDP"],
                outputs="media_gbif@pandas",
                name="from_media_to_media_gbif_node",
            ),
            node(  
                func=from_deployments_to_deployments_gbif,
                inputs=["deployments@pamDP"],
                outputs="deployments_gbif@pandas",
                name="from_deployments_to_deployments_gbif_node",
            ),
            node(  
                func=from_observations_to_observations_gbif,
                inputs=["observations@pamDP"],
                outputs="observations_gbif@pandas",
                name="from_observations_to_observations_gbif_node",
            ),
            node(  
                func=from_deployments_to_CSA_eventos,
                inputs=[
                    "deployments@pamDP",
                    "media@pamDP",
                    "field_deployments_sheet@pandas",
                ],
                outputs="CSA_eventos@pandas",
                name="from_deployments_to_CSA_eventos_node",
            ),
        ]
    )
