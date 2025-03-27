from pathlib import PurePosixPath
from typing import Any, Dict

import fsspec
import numpy as np

# from PIL import Image
from maad.sound import load, write

from kedro.io import AbstractDataset
from kedro.io.core import get_filepath_str, get_protocol_and_path
import os


class SoundDataset(AbstractDataset[np.ndarray, np.ndarray]):
    """``SoundDataset`` loads / save acoustic data from a given filepath as `numpy` array using maad.

    Example:
    ::

        >>> SoundDataset(filepath='/project/device/path.wav')
    """

    def __init__(self, filepath: str):
        """Creates a new instance of SoundDataset to load / save audio data for given filepath.

        Args:
            filepath: The location of the audio file to load / save data.
        """
        protocol, path = get_protocol_and_path(filepath)
        self._protocol = protocol
        self._filepath = PurePosixPath(os.path.normpath(path))
        self._fs = fsspec.filesystem(self._protocol)

    def _load(self) -> np.ndarray:
        """Loads data from the sound file.

        Returns:
            Data from the audio file as a numpy array
            sample rate
        """
        load_path = get_filepath_str(self._filepath, self._protocol)

        with self._fs.open(load_path, mode="rb") as f:
            recording, sr = load(f)
            return recording, sr

    def _save(self, data: np.ndarray) -> None:
        """Saves audio data to the specified filepath."""
        save_path = get_filepath_str(self._filepath, self._protocol)

        if not os.path.isdir(os.path.split(save_path)[0]):
            os.mkdir(os.path.split(save_path)[0])

        audio, sr = data
        with self._fs.open(save_path, mode="wb") as f:
            write(f, sr, audio, bit_depth=16)

    def _describe(self) -> Dict[str, Any]:
        """Returns a dict that describes the attributes of the dataset."""
        return dict(filepath=self._filepath, protocol=self._protocol)
