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


observations_pamdp_columns=[
'observationID' ,
'deploymentID', 
'mediaID',
'eventID',
'observationType',
'scientificName',
'bboxTime',
'bboxFrequency',
'bboxDuration',
'bboxBandwidth',
'classificationMethod',
'classifiedBy',
'classificationTimestamp',
'classificationProbability',
'observationComments',
]

observations_required_dictionary={
'observationID': True,
'deploymentID':True, 
'mediaID':False,
'eventID':False,
'observationType':True,
'scientificName':False,
'bboxTime':True,
'bboxFrequency':False,
'bboxDuration':False,
'bboxBandwidth':False,
'classificationMethod':False,
'classifiedBy':False,
'classificationTimestamp':False,
'classificationProbability':False,
'observationComments':False,
}

observations_schema_dictionary={
'observationID': str,
'deploymentID':str, 
'mediaID':str,
'eventID':str,
'observationType':str,#enum: animal, human voice, vehicle, silence, rain, wind, unknown, unclassified
'scientificName':str,
'bboxTime':'float64',
'bboxFrequency':'float64',
'bboxDuration':'float64',
'bboxBandwidth':'float64',
'classificationMethod':str,#enum: human, machine
'classifiedBy':str,
'classificationTimestamp':'datetime64[ns]',
'classificationProbability':'float64',
'observationComments':str,
}

observations_unique_dictionary={
'observationID' :True,
'deploymentID':False, 
'mediaID':False,
'eventID':False,
'observationType':False,
'scientificName':False,
'bboxTime':False,
'bboxFrequency':False,
'bboxDuration':False,
'bboxBandwidth':False,
'classificationMethod':False,
'classifiedBy':False,
'classificationTimestamp':False,
'classificationProbability':False,
'observationComments':False,
}

observations_enum_dictionary={
    'observationType':['animal', 'human' 'voice', 'vehicle', 'silence', 'rain', 'wind', 'unknown', 'unclassified'],
    'classificationMethod': ['human','machine']
}


class Observations(CSVPamDP):
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
            pamdp_columns=observations_pamdp_columns,
            required_dictionary=observations_required_dictionary,
            schema_dictionary=observations_schema_dictionary,
            unique_dictionary=observations_unique_dictionary,
            enum_dictionary=observations_enum_dictionary, 
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
