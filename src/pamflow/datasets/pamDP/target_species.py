from pathlib import PurePosixPath
from typing import Any, Dict, List
import fsspec
from kedro.io.core import get_filepath_str, get_protocol_and_path
import os
from kedro_datasets.pandas import CSVDataset
from kedro.io.core import (
    PROTOCOL_DELIMITER,
    AbstractVersionedDataset,
    DatasetError,
    Version,
    get_filepath_str,
    get_protocol_and_path,
)
import pandas as pd


class TargetSpecies(CSVDataset):
    def __init__(
        self,
        filepath: str,
        load_args: Dict[str, Any] | None = None,
        save_args: Dict[str, Any] | None = None,
        version: Version | None = None,
        credentials: Dict[str, Any] | None = None,
        fs_args: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ):
        super().__init__(
            filepath=filepath,
            load_args=load_args,
            save_args=save_args,
            version=version,
            credentials=credentials,
            fs_args=fs_args,
            metadata=metadata,
        )
        
        self.filepath = filepath

    def _load(self):
        if os.path.isfile(self.filepath):
            df = super()._load()
        else:
            df = pd.DataFrame({'scientificName':[]})
        
        if 'scientificName' not in df.columns:
            raise ValueError(
                    f"Target species should have a column called scientificName \n it has {df.columns} instead"
                )
        return df

    def _save(self, df):
        if 'scientificName' not in df.columns:
            raise ValueError(
                    f"Target species should have a column called scientificName \n it has {df.columns} instead"
                )
        super()._save(df)
