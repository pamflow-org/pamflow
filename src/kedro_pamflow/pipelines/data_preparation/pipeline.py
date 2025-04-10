from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    get_media_file,
    get_media_summary,
    plot_sensor_deployment,
    plot_sensor_location,
    get_timelapse,
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
                func=plot_sensor_deployment,
                inputs=["media@pamDP"],
                outputs=[
                    "sensor_deployment_figure@matplotlib",
                    "sensor_deployment_data@pandas",
                ],
                name="plot_sensor_deployment_node",
            ),
            node(  # Log
                func=field_deployments_sheet_to_deployments,
                inputs=["field_deployments_sheet@pandas", "media_summary@pandas"],
                outputs="deployments@pamDP",
                name="field_deployments_sheet_to_deployments_node",
            ),
            node(  # Log
                func=plot_sensor_location,
                inputs=["media_summary@pandas", "deployments@pamDP", "params:preprocess_plot"],
                outputs="sensor_location@matplotlib",
                name="plot_sensor_location_node",
            ),
            node(
                func=get_timelapse,
                inputs=[
                    "sensor_deployment_data@pandas",
                    "media@pamDP",
                    "params:timelapse.sample_length",
                    "params:timelapse.sample_period",
                    "params:preprocess_plot",
                ],
                outputs=[
                    "timelapse@PartitionedAudio",
                    "timelapse_spectrograms@PartitionedImage",
                ],
                name="get_timelapse_node",
            ),
        ]
    )
