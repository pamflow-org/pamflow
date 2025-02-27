from pathlib import PurePosixPath
from typing import Any, Dict
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


media_pamdp_columns=[
'mediaID' ,
'deploymentID' ,
'captureMethod',
'timestamp' ,
'filePath' ,
'filePublic' ,
'fileName',
'fileMediatype' ,
'sampleRate',
'bitDepth',
'fileLength',
'favorite',
'mediaComments'
]

required_dictionary={'mediaID' :True,
'deploymentID' :True,
'captureMethod':False,
'timestamp' :True,
'filePath' :True,
'filePublic' :True,
'fileName':True,
'fileMediatype' :True,
'sampleRate':True,
'bitDepth':True,
'fileLength':True,
'favorite':False,
'mediaComments':False,}

schema_dictionary={
'mediaID' :str,
'deploymentID' :str,
'captureMethod':str,# toca hacer prueba a parte para que verifique que solo están los valores activityDetection, timeLapse
'timestamp' :'datetime64[ns]', #toca hacer prueba a parte para que verifique ISO8601
'filePath':str,
'filePublic' :'bool', #hacer prueba previa de que tenga solo dos valores únicos
'fileName':str,
'fileMediatype' :str,
'sampleRate':'float64',
'bitDepth':'int64',
'fileLength':'float64',
'favorite':'bool', #hacer prueba previa de que tenga solo dos valores únicos
'mediaComments':'str'
}

unique_dictionary={
'mediaID' :True,
'deploymentID' :False,
'captureMethod':False,
'timestamp' :False,
'filePath' :False,
'filePublic' :False,
'fileName':False,
'fileMediatype' :False,
'sampleRate':False,
'bitDepth':False,
'fileLength':False,
'favorite':False,
'mediaComments':False
}


class Media(CSVDataset):
    def __init__(self, 
    filepath: str, 
    load_args: Dict[str, Any] | None = None, 
    save_args: Dict[str, Any] | None = None, 
    version: Version| None = None,
    credentials: Dict[str, Any] | None = None, 
    fs_args: Dict[str, Any] | None = None, 
    metadata: Dict[str, Any] | None = None
    ):
        super().__init__(
            filepath=filepath, 
            load_args=load_args, 
            save_args=save_args,
            version=version ,
            credentials=credentials, 
            fs_args=fs_args, 
            metadata=metadata
        )
    
    def _load(self):
        df = super()._load()
         # 1. Check column names & order
        if list(df.columns) != media_pamdp_columns:
            if set(df.columns) == set(media_pamdp_columns):
                raise ValueError(f"Column order mismatch. Expected order {media_pamdp_columns}, got {list(df.columns)}")
            else:
                raise ValueError(f"Column mismatch. There are extra or missing columns. \n Expected columns {media_pamdp_columns}, got {list(df.columns)}")

        # 2. Check column types
        for col, dtype in self.schema.items():
            if not pd.api.types.is_dtype_equal(df[col].dtype, dtype):
                raise TypeError(f"Column {col} has wrong type. Expected {dtype}, got {df[col].dtype}")

        # 3. Check mandatory columns for nulls
        for col in self.mandatory_columns:
            if df[col].isnull().any():
                raise ValueError(f"Mandatory column {col} contains null values.")

        # 4. Check unique constraints
        for col in self.unique_columns:
            if df[col].duplicated().any():
                raise ValueError(f"Column {col} has duplicate values but should be unique.")
        return df

    def _save(self,data):
        super()._save(data)
