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


deployments_pamdp_columns=[
"deploymentID",
"locationID",
"locationName",
"latitude",
"longitude",
"coordinateUncertainty",
"deploymentStart",
"deploymentEnd",
"setupBy",
"recorderID",
"recorderModel",
"recorderHeight",
"recorderConfiguration",
"habitat",
"deploymentGroups",
"deploymentComments",
]

deployments_required_dictionary={
"deploymentID":True,
"locationID":False,
"locationName":False,
"latitude":True,
"longitude":True,
"coordinateUncertainty":False,
"deploymentStart":True,
"deploymentEnd":True,
"setupBy":False,
"recorderID":False,
"recorderModel":True,
"recorderHeight":False,
"recorderConfiguration":True,
"habitat":False,
"deploymentGroups":False,
"deploymentComments":False,

}

deployments_schema_dictionary={
"deploymentID":str,
"locationID":str,#no estoy seguro
"locationName":str,
"latitude":'float64',
"longitude":'float64',
"coordinateUncertainty":'float64',
"deploymentStart":'datetime64[ns]',
"deploymentEnd":'datetime64[ns]',
"setupBy":str,
"recorderID":str,
"recorderModel":str,
"recorderHeight":'float64',
"recorderConfiguration":str,
"habitat":str,
"deploymentGroups":str,
"deploymentComments":str,
}

deployments_unique_dictionary={
"deploymentID":True,
"locationID":False,
"locationName":False,
"latitude":False,
"longitude":False,
"coordinateUncertainty":False,
"deploymentStart":False,
"deploymentEnd":False,
"setupBy":False,
"recorderID":False,
"recorderModel":False,
"recorderHeight":False,
"recorderConfiguration":False,
"habitat":False,
"deploymentGroups":False,
"deploymentComments":False,
}



class Deployments(CSVPamDP):
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
            pamdp_columns=deployments_pamdp_columns,
            required_dictionary=deployments_required_dictionary,
            schema_dictionary=deployments_schema_dictionary,
            unique_dictionary=deployments_unique_dictionary,
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
