from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    plot_sensor_performance,
    plot_sensor_location,
    get_timelapse
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            
            node(  # Log
                func=plot_sensor_performance,
                inputs=["media@pamDP"],
                outputs=[
                    "sensor_performance_figure@matplotlib",
                    "sensor_performance_data@pandas",
                ],
                name="plot_sensor_performance_node",
            ),
            node(  # Log
                func=plot_sensor_location,
                inputs=["media_summary@pandas","deployments@pamDP","params:quality_control_plot"],
                outputs="sensor_location@matplotlib",
                name="plot_sensor_location_node",
            ),
            
            node(
                func=get_timelapse,
                inputs=[
                    "sensor_performance_data@pandas",
                    "media@pamDP",
                    "params:timelapse.sample_length",
                    "params:timelapse.sample_period",
                    "params:quality_control_plot",
                ],
                outputs=[
                    "timelapse@PartitionedAudio",
                    "timelapse_spectrograms@PartitionedImage",
                ],
                name="get_timelapse_node",
            ),
        ]
    )
