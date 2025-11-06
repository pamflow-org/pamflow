#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""

import os
from maad import util
import pandas as pd
import logging
import numpy as np
from pamflow.datasets.pamDP.deployments import deployments_pamdp_columns

logger = logging.getLogger(__name__)

def get_media_file(input_path, field_deployments_sheet):
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
    sensors_in_field_deployments=field_deployments_sheet['deploymentID'].unique().tolist()
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

    # Ensure timestamp is in datetime format and estimate duty cycle
    media["timestamp"] = pd.to_datetime(media.timestamp)
    media["diff"] = media["timestamp"].sort_values().diff()
    
    # Summarize by deploymentID
    media_summary = (
        media.groupby("deploymentID")
        .agg(
            date_ini=("timestamp", "min"),
            date_end=("timestamp", "max"),
            n_recordings=("deploymentID", "count"),
            time_diff=("diff", "median"),
            sample_length=("fileLength", "median"),
            sample_rate=("sampleRate", lambda x: x.mode().iloc[0] if not x.mode().empty else None),
        )
        .reset_index()
    )
    
    # Compute duration of each deployment
    media_summary["duration"] = media_summary["date_end"] - media_summary["date_ini"]
    
    return media_summary


def field_deployments_sheet_to_deployments(field_deployments, media_summary):
    """Converts user-provided deployments templates into a standardized deployments DataFrame.

    This node processes a user-provided template and combines it with media summary data
    to generate a deployments DataFrame following the pamDP.deployment format. The inputs
    correspond to the catalog entries `field_deployments@pandas` and `media_summary@pandas`.
    The output is stored in the catalog as `deployments@pamDP`.

    Parameters
    ----------
    field_deployments : pandas.DataFrame
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

    logger.info("Converting field deployments sheet to pamDP deployments format...")
    
    # -- 1. Create deployments dataframe following pamDP standards -- #

    # Create a new DataFrame with the schema
    deployments = pd.DataFrame(columns=deployments_pamdp_columns)

    # -- 2. Read the data from field_deployments and adjust as necessary -- #
    # Adjust and combine recordists names
    field_deployments["setupBy"] = (
        field_deployments["setupByName"]
        + field_deployments["setupByLastName"]
    )

    # Combine date and time columns into datetime fields
    field_deployments['deploymentStart'] = pd.to_datetime(
        field_deployments["deploymentStartDate"].astype(str) + ' ' + 
        field_deployments["deploymentStartTime"].astype(str)
    )
    
    field_deployments['deploymentEnd'] = pd.to_datetime(
        field_deployments["deploymentEndDate"].astype(str) + ' ' + 
        field_deployments["deploymentEndTime"].astype(str)
    )

    # 3 -- Map existing fields from field_deployments to deployments -- #
    # Populate deployments DataFrame
    for column in deployments_pamdp_columns:
        if column in field_deployments.columns:
            deployments[column] = field_deployments[column]
        else:
            deployments[column] = None

    n_recordings = media_summary["n_recordings"].sum()
    logger.info(f"Done! {len(deployments)} deployments with {n_recordings} recordings saved to pamDP format.")

    return deployments
