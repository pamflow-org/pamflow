#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""

import os
from maad import util
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_media_file(input_pat, field_deployments_sheet):
    """Retrieves and processes metadata from media files in the given directory.

    Parameters
    ----------
    input_path : str
        Path to the directory containing a folder for each sensor
        and the corresponding wav files. Specified in parameters.yml
        as DEVICES_ROOT_DIRECTORY.
    field_deployments_sheet : pandas.DataFrame
        A DataFrame containing user-provided deployments information. Loaded from the catalog
        entry `field_deployments_sheet@pandas`.


    Returns
    -------
    media : pandas DataFrame
        Processed metadata of media files with standardized column names.
        The DataFrame follows the pamDP.media format. Stored in catalog as
        media@pamDP.
    """

    # add_file_prefix(folder_name=input_path,
    #                recursive=True
    #                )
    logger.info(f"Preparing data from {input_path}...")
    # checking consistency between sensors found on audio root directory and field deployments sheet
    sensors_in_audio_root_directory=os.listdir(input_path)
    sensors_in_field_deployments=field_deployments_sheet['Indicador de evento'].unique().tolist()
    if set(sensors_in_audio_root_directory)!=set(sensors_in_field_deployments):
    missing_in_field_deployments = set(sensors_in_audio_root_directory) - set(sensors_in_field_deployments)
    if missing_in_field_deployments:
        logger.warning(
            f"Deployments {', '.join(missing_in_field_deployments)}, "
            "found on Audio Root Directory, won't be fully processed as they are not listed on Field Deployments Sheet."
        )

    missing_in_audio = set(sensors_in_field_deployments) - set(sensors_in_audio_root_directory)
    if missing_in_audio:
        logger.warning(
            f"Deployments {', '.join(missing_in_audio)}, "
            "found on Field Deployments Sheet, won't be fully processed because they have no corresponding folder "
            "on Audio Root Directory."
        )
    metadata = util.get_metadata_dir(input_path, False)
    metadata.dropna(inplace=True)  # remove problematic files
    columns_names_dict = {
        "path_audio": "filePath",
        "fname": "mediaID",
        "bits": "bitDepth",
        "sample_rate": "sampleRate",
        "length": "fileLength",
        "channels": "numChannels",
        "sensor_name": "deploymentID",
        "date": "timestamp",
    }
    media = metadata.rename(columns=columns_names_dict)
    media["fileName"] = media["filePath"].str.split(os.sep).str[-1]
    media["fileMediatype"] = "audio/WAV"
    media["mediaComments"] = None
    media["favorite"] = None
    media["filePublic"] = False  
    media["captureMethod"] = "activityDetection"
    media["fileLength"] = media["fileLength"].astype(float).round(3)
    # checking consistency between sensors found on audio root directory and media
    sensors_in_media=media['deploymentID'].unique().tolist()
    missing_in_media=set(sensors_in_audio_root_directory)-set(sensors_in_media)
    if missing_in_media:
        logger.warning(
                f"Deployments {', '.join(missing_in_media)} "
                " won't be processed as the corresponding folders on Audio Root Directory were empty or none of the WAV files within met the file name format."
            )
    return media.drop(columns=["time", "fsize", "samples"])


def get_media_summary(media):
    """Summarizes metadata of acoustic sampling for each deployment.

    This node processes a metadata DataFrame following the pamDP.media data standards
    and generates a summary for each deployment. The input corresponds to the catalog
    entry `media@pamDP`, and the output is stored in the catalog as `media_summary@pandas`.

    Parameters
    ----------
    media : pandas.DataFrame
        A DataFrame containing metadata of media files, following the pamDP.media format.
        This is typically loaded from the catalog entry `media@pamDP`.

    Returns
    -------
    pandas.DataFrame
        A summary DataFrame for each deployment, including the start and end dates,
        number of recordings, median time difference between recordings, and other
        statistics. This is stored in the catalog as `media_summary@pandas`.
    """

    media["timestamp"] = pd.to_datetime(media.timestamp)

    media["diff"] = media["timestamp"].sort_values().diff()
    media_summary = (
        media.groupby("deploymentID")
        .agg(
            date_ini=("timestamp", "min"),
            date_end=("timestamp", "max"),
            n_recordings=("deploymentID", "count"),
            time_diff=("diff", "median"),
            sample_length=("fileLength", "median"),
            sample_rate=("sampleRate", "median"),
        )
        .reset_index()
    )
    media_summary["duration"] = media_summary["date_end"] - media_summary["date_ini"]
    return media_summary


def field_deployments_sheet_to_deployments(plantilla_usuario, media_summary):
    """Converts user-provided deployments templates into a standardized deployments DataFrame.

    This node processes a user-provided template and combines it with media summary data
    to generate a deployments DataFrame following the pamDP.deployment format. The inputs
    correspond to the catalog entries `plantilla_usuario@pandas` and `media_summary@pandas`.
    The output is stored in the catalog as `deployments@pamDP`.

    Parameters
    ----------
    plantilla_usuario : pandas.DataFrame
        A DataFrame containing user-provided deployments information. Loaded from the catalog
        entry `field_deployments_sheet@pandas`.

    media_summary : pandas.DataFrame
        A DataFrame summarizing metadata of acoustic sampling for each deployments. Loaded from
        the catalog entry `media_summary@pandas`.

    Returns
    -------
    pandas.DataFrame
        A standardized deployments DataFrame following the pamDP.deployments format. Stored in
        the catalog as `deployments@pamDP`.
    """
    plantilla_usuario["Nombre del instalador+Apellido  del instalador"] = (
        plantilla_usuario["Nombre del instalador"]
        + plantilla_usuario["Apellido  del instalador"]
    )

    columns_names_map = {
        "Indicador de evento": "deploymentID",
        "Localidad": "locationName",
        "Latitud": "latitude",
        "Longitud": "longitude",
        "Equipo de grabación": "recorderModel",
        "Comentario de sonido": "deploymentComments",
        "Configuración de muestreo": "recorderConfiguration",
        "Hábitat": "habitat",
        "Nombre del instalador+Apellido  del instalador": "setupBy",
        "Altura de la grabadora respecto al suelo": "recorderHeight",
    }

    deployments = plantilla_usuario[list(columns_names_map.keys())
                                   +["Fecha inicial","Fecha final", 'Hora inicial','Hora final'    ]
    ].rename(
        columns=columns_names_map
    )

    deployments['deploymentStart']=deployments["Fecha inicial"].astype(str) + ' ' + deployments['Hora inicial'].astype(str)
    deployments['deploymentEnd'  ]=deployments["Fecha final"  ].astype(str) + ' ' + deployments['Hora final'  ].astype(str)
    deployments=deployments.astype({'deploymentStart':'datetime64[ns]',
                    'deploymentEnd' :'datetime64[ns]'
                })

    deployments=deployments.drop(columns=['Fecha inicial','Fecha final', 'Hora inicial','Hora final'])

    deployments["recorderID"] = None
    deployments["locationID"] = deployments["locationName"]
    deployments["coordinateUncertainty"] = None
    deployments["deploymentGroups"] = None

    n_recordings = media_summary["n_recordings"].sum()
    media_summary = media_summary[["deploymentID", "date_ini", "date_end"]]

    deployments = deployments.merge(media_summary, on="deploymentID", how="left")

    deployments["deploymentStart"] = deployments["deploymentStart"].combine_first(
        deployments["date_ini"]
    )
    deployments["deploymentEnd"] = deployments["deploymentEnd"].combine_first(
        deployments["date_end"]
    )

    deployments = deployments.dropna(
        subset=["deploymentStart", "deploymentEnd", "deploymentID"]
    )

    deployments = deployments.drop(columns=["date_ini", "date_end"])
    
    logger.info(f"Done! {len(deployments)} deployments with {n_recordings} recordings saved to pamDP format.")

    return deployments
