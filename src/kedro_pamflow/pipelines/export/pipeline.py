from kedro.pipeline import Pipeline, node, pipeline
from .nodes import from_deployments_to_DwC, from_deployments_to_CSA_eventos


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(  # Log
                func=from_deployments_to_DwC,
                inputs=["deployments@pamDP"],
                outputs="DwC_eventos@pandas",
                name="from_deployments_to_DwC_node",
            ),
            node(  # Log
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
