from pathlib import PurePosixPath
from typing import Any, Dict, List
import fsspec
from kedro.io.core import get_filepath_str, get_protocol_and_path
import os
from kedro_datasets.pandas import ExcelDataset
from kedro.io.core import (
    PROTOCOL_DELIMITER,
    AbstractVersionedDataset,
    DatasetError,
    Version,
    get_filepath_str,
    get_protocol_and_path,
)
import pandas as pd

mandatory_columns = [
    'Indicador de evento',	
    'Latitud',
	'Longitud',
	'Fecha inicial',
	'Fecha final',
	'Hora inicial',
	'Hora final',
	'Equipo de grabación',
	'Nombre del instalador',
    'Apellido  del instalador',
	'Hábitat',
    'Configuración de muestreo',
    'Altura de la grabadora respecto al suelo',
    'test'
    ]

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


class FieldDeployments(ExcelDataset):
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


        self.pamdp_columns = [
                                "deploymentID",
                                "locationName",
                                "latitude",
                                "longitude",
                                "coordinateUncertainty",
                                "deploymentStartDate",
                                "deploymentEndDate",
                                "deploymentStartTime",
                                "deploymentEndTime",
                                "setupByName",
                                "setupByLastName",
                                "recorderModel",
                                "recorderHeight",
                                "recorderConfiguration",
                                "habitat",
                                "deploymentComments",

                            ]
        self.required_dictionary = {
                                "deploymentID": True,
                                "locationName": False,
                                "latitude": True,
                                "longitude": True,
                                "coordinateUncertainty": False,
                                "deploymentStartDate":True,
                                "deploymentEndDate":True,
                                "deploymentStartTime":True,
                                "deploymentEndTime":True,
                                "setupByName":False,
                                "setupByLastName":False,
                                "recorderModel": True,
                                "recorderHeight": False,
                                "recorderConfiguration": True,
                                "habitat": False,
                                "deploymentComments": False,
                            }

        self.unique_dictionary = {
                                "deploymentID": True,
                                "locationName": False,
                                "latitude": False,
                                "longitude": False,
                                "coordinateUncertainty": False,
                                "deploymentStartDate":False,
                                "deploymentEndDate":False,
                                "deploymentStartTime":False,
                                "deploymentEndTime":False,
                                "setupByName":False,
                                "setupByLastName":False,
                                "recorderModel": False,
                                "recorderHeight": False,
                                "recorderConfiguration": False,
                                "habitat": False,
                                "deploymentComments": False,
                              }

    def _load(self):
        df = super()._load()
        # 1. Check column names & order
        if not set( set(self.pamdp_columns) ).issubset(df.columns):
                raise ValueError(
                    f"Missing columns for field_deployments format: \n list of missing columns {set(self.pamdp_columns) - set(df.columns)}"
                )
        
        # 2. Check mandatory columns for nulls
        for col, mandatory in self.required_dictionary.items():
            if df[col].isnull().any() and mandatory:
                raise ValueError(f"Mandatory column {col} contains null values.")

        # 3. Check unique constraints
        for col, unique_constraint in self.unique_dictionary.items():
            if df[col].duplicated().any() and unique_constraint:
                raise ValueError(
                    f"Column {col} has duplicate values but should be unique."
                )
    

        return df

    def _save(self, df):
        # 1. Check column names & order
        if set(df.columns) != set(self.pamdp_columns):
            if set(df.columns).issubset(set(self.pamdp_columns)):
                raise ValueError(
                    f"Missing columns for field_deployments format: \n list of missing columns {set(self.pamdp_columns) - set(df.columns)}"
                )
        
        # 2. Check mandatory columns for nulls
        for col, mandatory in self.required_dictionary.items():
            if df[col].isnull().any() and mandatory:
                raise ValueError(f"Mandatory column {col} contains null values.")

        # 3. Check unique constraints
        for col, unique_constraint in self.unique_dictionary.items():
            if df[col].duplicated().any() and unique_constraint:
                raise ValueError(
                    f"Column {col} has duplicate values but should be unique."
                )
        
        super()._save(df)

