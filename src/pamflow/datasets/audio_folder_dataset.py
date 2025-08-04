from pathlib import PurePosixPath, Path
from typing import Any, Dict

import fsspec

import os

from kedro.io import AbstractDataset
from kedro_datasets.partitions import PartitionedDataset
from kedro.io.core import get_filepath_str, get_protocol_and_path
from kedro_pamflow.datasets.audio_dataset import SoundDataset


class AudioFolderDataset(AbstractDataset[Dict[str, Any], Dict[str, Any]]):
    def __init__(self, main_folder_path: str):
        """Creates a new instance of SoundDataset to load / save audio data for given filepath.

        Args:
            filepath: The location of the audio file to load / save data.
        """
        protocol, mainfolderpath = get_protocol_and_path(main_folder_path)
        self._protocol = protocol
        self._mainfolderpath = PurePosixPath(mainfolderpath)
        self._fs = fsspec.filesystem(self._protocol)

    def _load(self):
        subfolder_names = [
            subfolder_name
            for subfolder_name in os.listdir(self._mainfolderpath)
            if os.path.isdir(os.path.join(self._mainfolderpath, subfolder_name))
        ]

        wav_paths_dict = {}
        for subfolder_name in subfolder_names:
            subfolder_path = os.path.join(self._mainfolderpath, subfolder_name)
            wav_files = []
            for root, dirs, files in os.walk(subfolder_path):
                for file in files:
                    if file.lower().endswith(".wav"):
                        wav_file_path = os.path.join(root, file)
                        wav_file_name = (
                            os.path.split(wav_file_path)[-1]
                            .replace(".wav", "")
                            .replace(".WAV", "")
                        )
                        wav_files.append((wav_file_name, wav_file_path))
                wav_paths_dict[subfolder_name] = dict(wav_files)

        partitioned_dataset_dict = {}
        for subfolder_name, sub_dict in wav_paths_dict.items():
            partitioned_dataset = [
                (wav_file_name, SoundDataset(wav_file_path).load())
                for wav_file_name, wav_file_path in sub_dict.items()
            ]
            partitioned_dataset_dict[subfolder_name] = dict(partitioned_dataset)

        return partitioned_dataset_dict

    def _save(self, subfolders_dictionary):
        if os.path.isdir(self._mainfolderpath):
            for root, dirs, files in os.walk(self._mainfolderpath, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self._mainfolderpath)
        os.mkdir(self._mainfolderpath)
        for subfolder_name in subfolders_dictionary.keys():
            subfolder_path = os.path.join(self._mainfolderpath, subfolder_name)
            os.mkdir(os.path.normpath(subfolder_path))

            # print(subfolder_name, subfolder_path)
            partitioned_dataset = PartitionedDataset(
                path=subfolder_path,
                dataset=SoundDataset,
                filename_suffix=".WAV",
            )

            partitioned_dataset.save(subfolders_dictionary[subfolder_name])

    def _describe(self):
        """Returns a dict that describes the attributes of the dataset."""
        return dict(mainfolderpath=self._mainfolderpath, protocol=self._protocol)
