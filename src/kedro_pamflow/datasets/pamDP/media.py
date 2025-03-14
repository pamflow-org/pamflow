from pathlib import PurePosixPath
from typing import Any, Dict
import fsspec
from kedro.io.core import get_filepath_str, get_protocol_and_path
import os
#from kedro_datasets.pandas import CSVDataset
from .CSVPamDP import CSVPamDP
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
#'filePublic' ,
'fileName',
'fileMediatype' ,
'sampleRate',
'bitDepth',
'fileLength',
'numChannels',
'favorite',
'mediaComments'
]

media_required_dictionary={'mediaID' :True,
'deploymentID' :True,
'captureMethod':False,
'timestamp' :True,
'filePath' :True,
#'filePublic' :True,
'fileName':True,
'fileMediatype' :True,
'sampleRate':True,
'bitDepth':True,
'fileLength':True,
'numChannels':True,
'favorite':False,
'mediaComments':False,}

media_schema_dictionary={
'mediaID' :str,
'deploymentID' :str,
'captureMethod':str,# toca hacer prueba a parte para que verifique que solo están los valores activityDetection, timeLapse
'timestamp' :'datetime64[ns]', #toca hacer prueba a parte para que verifique ISO8601
'filePath':str,
#'filePublic' :'bool', #hacer prueba previa de que tenga solo dos valores únicos
'fileName':str,
'fileMediatype' :str,
'sampleRate':'float64',
'bitDepth':'int64',
'fileLength':'float64',
'numChannels':'int64',
'favorite':'bool', #hacer prueba previa de que tenga solo dos valores únicos
'mediaComments':'str'
}

media_unique_dictionary={
'mediaID' :True,
'deploymentID' :False,
'captureMethod':False,
'timestamp' :False,
'filePath' :False,
#'filePublic' :False,
'fileName':False,
'fileMediatype' :False,
'sampleRate':False,
'bitDepth':False,
'fileLength':False,
'numChannels':False,
'favorite':False,
'mediaComments':False
}

media_enum_dictionary={
    'captureMethod':['activityDetection', 'timeLapse'],
    'favorite': [True,False]
}


class Media(CSVPamDP):
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
            pamdp_columns=media_pamdp_columns,
            required_dictionary=media_required_dictionary,
            schema_dictionary=media_schema_dictionary,
            unique_dictionary=media_unique_dictionary,
            enum_dictionary=media_enum_dictionary,
            filepath=filepath, 
            load_args=load_args, 
            save_args=save_args,
            version=version ,
            credentials=credentials, 
            fs_args=fs_args, 
            metadata=metadata,
            
        )
    
    def _load(self):
        df=super()._load()
        
        return df
    def _save(self,df):
        
        super()._save(df)
