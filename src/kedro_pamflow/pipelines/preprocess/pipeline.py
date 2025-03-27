from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    get_media_file,
    get_media_summary,
    plot_sensor_deployment,
    plot_sensor_location,
    get_timelapse,
    plantilla_usuario_to_deployment,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(  # Log
                func=get_media_file,
                inputs=["params:DEVICES_ROOT_DIRECTORY"],
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
                func=plot_sensor_deployment,
                inputs=["media@pamDP"],
                outputs=[
                    "sensor_deployment_figure@matplotlib",
                    "sensor_deployment_data@pandas",
                ],
                name="plot_sensor_deployment_node",
            ),
            node(  # Log
                func=plantilla_usuario_to_deployment,
                inputs=["plantilla_usuario_fdm@pandas", "media_summary@pandas"],
                outputs="deployment@pamDP",
                name="plantilla_usuario_to_deployment_node",
            ),
            node(  # Log
                func=plot_sensor_location,
                inputs=["media_summary@pandas", "deployment@pamDP", "params:plot"],
                outputs="sensor_location@matplotlib",
                name="plot_sensor_location_node",
            ),
            node(
                func=get_timelapse,
                inputs=[
                    "sensor_deployment_data@pandas",
                    "media@pamDP",
                    "params:preprocessing.sample_length",
                    "params:preprocessing.sample_period",
                    "params:plot",
                ],
                outputs=[
                    "timelapse@PartitionedAudio",
                    "timelapse_spectrograms@PartitionedImage",
                ],
                name="get_timelapse_node",
            ),
        ]
    )
