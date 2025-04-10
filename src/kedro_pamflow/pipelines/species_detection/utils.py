import os
from maad import sound
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from contextlib import redirect_stdout
import concurrent.futures


def species_detection_single_file(wav_file_path, lat, lon, mediaID, deploymentID):
    """Performs species detection on a single media file.

    This utility function processes a single media file to detect species based on
    its audio content. The function uses the file's metadata, including geographic
    location and deployment information, to enhance detection accuracy. The output
    is a list of detected species observations for the given file. The detections
    are performed using birdnetlib, a Python library for BirdNET-Analyzer.

    Parameters
    ----------
    file_path : str
        The path to the media file to be processed.

    latitude : float
        The latitude of the deployment location where the media file was recorded.

    longitude : float
        The longitude of the deployment location where the media file was recorded.

    media_id : str
        A unique identifier for the media file.

    deployment_id : str
        A unique identifier for the deployment associated with the media file.

    Returns
    -------
    list
        A list of dictionaries, where each dictionary represents a detected species
        observation. Each observation includes details such as scientific name,
        start time, end time, confidence score, and other relevant metadata.
    """
    with open('/dev/null', 'w') as fnull, redirect_stdout(fnull):  # Suppress print messages
        # Load and initialize the BirdNET-Analyzer models.
        analyzer = Analyzer()
        recording = Recording(
            analyzer,
            wav_file_path,
            lat=lat,
            lon=lon,
        )
    
        recording.analyze()
    
    # species_detections is a list of dictionaries.
    # One  dictionary for each detection having the following keys:
    # dict_keys(['common_name', 'scientific_name', 'start_time', 'end_time', 'confidence', 'label'])
    species_detections = recording.detections

    # Four keys are added to each dictionary:
    # mediaID, deploymentID, classifiedBy
    species_detections_extra_keys = [
        {
            **detection_dict,
            **{
                "mediaID": mediaID,
                "deploymentID": deploymentID,
                "classifiedBy": f"Birdnet {analyzer.version}",
            },
        }
        for detection_dict in species_detections
    ]
    return species_detections_extra_keys


def trim_audio(start_time, end_time, path_audio, segments_file_name):
    """Trims an audio file to create a segment based on the specified start and end times.

    This utility function extracts a segment from an audio file based on the provided
    start and end times. The trimmed audio segment is returned along with its sample rate
    and a modified file name for the segment.

    Parameters
    ----------
    start_time : float
        The start time (in seconds) of the audio segment to be extracted.

    end_time : float
        The end time (in seconds) of the audio segment to be extracted.

    path_audio : str
        The file path to the original audio file.

    segments_file_name : str
        The file name to be used for the trimmed audio segment. The file name will be
        customized to exclude the file extension.

    Returns
    -------
    tuple
        A tuple containing:
        - str: The modified file name for the audio segment (without the file extension).
        - tuple: A tuple containing the trimmed audio numpy array and its sample rate.
    """
    audio_array, sr = sound.load(path_audio)
    trimmed_audio = audio_array[int(start_time * sr) : int(end_time * sr)]
    return (segments_file_name[0:-4], (trimmed_audio, sr))
