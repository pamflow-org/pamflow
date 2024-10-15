from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    get_audio_metadata, 
    metadata_summary,
    plot_sensor_deployment,
    plot_sensor_location,
    get_timelapse
    )





def create_pipeline(**kwargs):
    return Pipeline(
        [
          
            node( # Log
                func=get_audio_metadata,
                inputs=[ 'params:DEVICES_ROOT_DIRECTORY'],
                outputs="audio_metadata@pandas",
                name="get_audio_metadata_node",
            ),

            node( # Log
                func=metadata_summary,
                inputs=[ "audio_metadata@pandas"],
                outputs="audio_metadata_summary@pandas",
                name="metadata_summary_node",
            ),
            node( # Log
                func=plot_sensor_deployment,
                inputs=[ "audio_metadata@pandas"],
                outputs=["sensor_deployment_figure@matplotlib","sensor_deployment_data@pandas"],
                name="plot_sensor_deployment_node",
            ),
            node( # Log
                func=plot_sensor_location,
                inputs=[ "audio_metadata@pandas",
                "audio_metadata_summary@pandas", 
                "formato_migracion@pandas",
                "params:plot",
                "params:formato_migracion_parameters"],
                outputs="sensor_location@matplotlib",
                name="plot_sensor_location_node",
            ),
            node(
                func=get_timelapse,
                inputs=['sensor_deployment_data@pandas',
                        'audio_metadata@pandas',             
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
