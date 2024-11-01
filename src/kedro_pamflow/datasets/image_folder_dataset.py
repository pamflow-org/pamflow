from pathlib import PurePosixPath, Path
from typing import Any, Dict
import os
import fsspec
from kedro.io import AbstractDataset
from kedro_datasets.partitions import PartitionedDataset
from kedro.io.core import get_filepath_str, get_protocol_and_path
from kedro_datasets.matplotlib import MatplotlibWriter

class ImageFolderDataset(AbstractDataset[Dict[str, Any], Dict[str, Any]]):
    

    def __init__(self, main_folder_path: str):
        """Creates a new instance of Folder of MatplotlibWriters to load / save images for given filepath.

        Args:
            filepath: The location of the images folder to load / save data.
        """
        protocol, mainfolderpath = get_protocol_and_path(main_folder_path)
        self._protocol = protocol
        self._mainfolderpath = PurePosixPath(mainfolderpath)
        self._fs = fsspec.filesystem(self._protocol)

    def _load(self):
        subfolder_names=[ subfolder_name 
                         for subfolder_name in os.listdir(self._mainfolderpath) 
                         if os.path.isdir(os.path.join(self._mainfolderpath, subfolder_name)) 
                        ]
        
        
        png_paths_dict={}
        for subfolder_name in subfolder_names:
            subfolder_path=os.path.join(self._mainfolderpath, subfolder_name)
            png_files=[]
            for root, dirs, files in os.walk(subfolder_path):
                for file in files:
                    if file.lower().endswith('.png'):
                        png_file_path=os.path.join(root, file)
                        png_file_name=os.path.split(png_file_path)[-1].replace('.png','')
                        png_files.append((png_file_name,png_file_path))
                png_paths_dict[subfolder_name]=dict(png_files)

        
        partitioned_dataset_dict={}
        for subfolder_name, sub_dict in png_paths_dict.items():
            partitioned_dataset=[(png_file_name,MatplotlibWriter(filepath=png_file_path)) for png_file_name,png_file_path in sub_dict.items()]
            partitioned_dataset_dict[subfolder_name]=dict(partitioned_dataset)
        
        return partitioned_dataset_dict




        



    
    def _save(self, subfolders_dictionary):
        if os.path.isdir(self._mainfolderpath):
            for root, dirs, files in os.walk(self._mainfolderpath,topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self._mainfolderpath)
        os.mkdir(self._mainfolderpath)
        for subfolder_name in subfolders_dictionary.keys():
            subfolder_path=os.path.join(self._mainfolderpath, subfolder_name) 
            os.mkdir(os.path.normpath(subfolder_path))

            
            partitioned_dataset = PartitionedDataset(
            path=subfolder_path,
            dataset=MatplotlibWriter,
            filename_suffix=".png",
            )
            
            partitioned_dataset.save(subfolders_dictionary[subfolder_name])
    
    def _describe(self):
        """Returns a dict that describes the attributes of the dataset."""
        return dict(mainfolderpath=self._mainfolderpath, protocol=self._protocol)