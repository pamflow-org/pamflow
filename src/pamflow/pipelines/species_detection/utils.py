import os
from maad import sound
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from contextlib import redirect_stdout
import concurrent.futures

# BirdNET Analyzer shared by all the tasks run in a process. Loading the model is
# expensive, so it is created once per worker (see `init_worker`) instead of once per file.
_ANALYZER = None
_ANALYZER_KEY = None


def _get_analyzer(classifier_model_path=None, classifier_labels_path=None):
    """Returns the process-level Analyzer, creating it only if needed."""
    global _ANALYZER, _ANALYZER_KEY
    key = (classifier_model_path, classifier_labels_path)
    if _ANALYZER is None or _ANALYZER_KEY != key:
        with open(os.devnull, "w") as fnull, redirect_stdout(fnull):
            _ANALYZER = Analyzer(
                classifier_model_path=classifier_model_path,
                classifier_labels_path=classifier_labels_path,
            )
        _ANALYZER_KEY = key
    return _ANALYZER


def init_worker(classifier_model_path=None, classifier_labels_path=None):
    """ProcessPoolExecutor initializer: loads the BirdNET model once per worker."""
    _get_analyzer(classifier_model_path, classifier_labels_path)


def species_detection_single_file(
    wav_file_path,
    lat,
    lon,
    mediaID,
    deploymentID,
    classifier_model_path=None,
    classifier_labels_path=None,
    min_conf=0.1,
):
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

    latitude : float or None
        The latitude of the deployment location where the media file was recorded.
        If None, detections are not filtered by location.

    longitude : float or None
        The longitude of the deployment location where the media file was recorded.
        If None, detections are not filtered by location.

    media_id : str
        A unique identifier for the media file.

    deployment_id : str
        A unique identifier for the deployment associated with the media file.

    min_conf : float, default 0.1
        Minimum BirdNET confidence for a detection to be kept.

    Returns
    -------
    list
        A list of dictionaries, where each dictionary represents a detected species
        observation. Each observation includes details such as scientific name,
        start time, end time, confidence score, and other relevant metadata.
    """
    with open(os.devnull, 'w') as fnull, redirect_stdout(fnull):  # Suppress print messages
        # Reuse the BirdNET-Analyzer loaded once per worker (loaded here if no initializer ran).
        analyzer = _get_analyzer(classifier_model_path, classifier_labels_path)
        # The analyzer keeps the species list of the previous recording: clear it so that
        # each file is processed exactly as with a fresh analyzer.
        if not analyzer.has_custom_species_list:
            analyzer.custom_species_list = []
        recording = Recording(
            analyzer,
            wav_file_path,
            lat=lat,
            lon=lon,
            min_conf=min_conf,
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
