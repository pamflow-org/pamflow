from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    get_audio_metadata, 
    metadata_summary,
    plot_sensor_deployment,
    plot_sensor_location,
    get_timelapse,
    plantilla_usuario_to_deployment
    )





def create_pipeline(**kwargs):
    return Pipeline(
        [
          
            node( # Log
                func=get_audio_metadata,
                inputs=[ 'params:DEVICES_ROOT_DIRECTORY'],
                outputs="media@pandas",
                name="get_audio_metadata_node",
            ),

            node( # Log
                func=metadata_summary,
                inputs=[ "media@pandas"],
                outputs="audio_metadata_summary@pandas",
                name="metadata_summary_node",
            ),
            node( # Log
                func=plot_sensor_deployment,
                inputs=[ "media@pandas"],
                outputs=["sensor_deployment_figure@matplotlib","sensor_deployment_data@pandas"],
                name="plot_sensor_deployment_node",
            ),
            node( # Log
                func=plantilla_usuario_to_deployment,
                inputs=[ 'plantilla_usuario_fdm@pandas'],
                outputs="deployment@pandas",
                name="plantilla_usuario_to_deployment_node",
            ),
            node( # Log
                func=plot_sensor_location,
                inputs=[ "media@pandas",
                "audio_metadata_summary@pandas", 
                "deployment@pandas",
                "params:plot",
                "params:deployment_parameters"],
                outputs="sensor_location@matplotlib",
                name="plot_sensor_location_node",
            ),
            node(
                func=get_timelapse,
                inputs=['sensor_deployment_data@pandas',
                        'media@pandas',             
                        'params:preprocessing.sample_length',
                        'params:preprocessing.sample_period',
                        'params:plot'                            
                        ],
                outputs=['timelapse@PartitionedAudio',
                'timelapse_spectrograms@PartitionedImage'],
                name='get_timelapse_node'
            )
            
        ]
    )
