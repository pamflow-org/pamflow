from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    from_deployments_to_DwC,
    from_deployments_to_CSA_eventos
    )





def create_pipeline(**kwargs):
    return Pipeline(
        [
          
            node( # Log
                func=from_deployments_to_DwC,
                inputs=[ 'deployment@pamDP'],
                outputs="DwC_eventos@pandas",
                name="from_deployments_to_DwC_node",
            ),
            node( # Log
                func=from_deployments_to_CSA_eventos,
                inputs=[ 'deployment@pamDP','media@pamDP','plantilla_usuario_fdm@pandas'],
                outputs="CSA_eventos@pandas",
                name="from_deployments_to_CSA_eventos_node",
            ),

            
            
        ]
    )
