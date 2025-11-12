from pathlib import PurePosixPath
from typing import Any, Dict
import fsspec
from kedro.io.core import get_filepath_str, get_protocol_and_path
import os

# from kedro_datasets.pandas import CSVDataset
from .CSVPamDP import CSVPamDP
from kedro.io.core import (
    PROTOCOL_DELIMITER,
    AbstractVersionedDataset,
    DatasetError,
    Version,
    get_filepath_str,
    get_protocol_and_path,
)


observations_pamdp_columns = [
    "observationID",
    "deploymentID",
    "mediaID",
    "eventID",
    "eventStart",
    "eventEnd",
    "frequencyLow",
    "frequencyHigh",
    "observationLevel",
    "observationType",
    "scientificName",
    "count",
    "lifeStage",
    "sex",
    "behavior",
    "individualID",
    "individualPositionRadius",
    "classificationMethod",
    "classifiedBy",
    "classificationTimestamp",
    "classificationProbability",
    "observationTags",
    "observationComments",
]

observations_required_dictionary = {
    "observationID": True,
    "deploymentID": True,
    "mediaID": False,
    "eventID": False,
    "eventStart": True,
    "eventEnd": True,
    "frequencyLow": False,
    "frequencyHigh": False,
    "observationLevel": True,
    "observationType": True,
    "scientificName": False,
    "count": False,
    "lifeStage": False,
    "sex": False,
    "behavior": False,
    "individualID": False,
    "individualPositionRadius": False,
    "classificationMethod": False,
    "classifiedBy": False,
    "classificationTimestamp": False,
    "classificationProbability": False,
    "observationTags": False,
    "observationComments": False
}

observations_schema_dictionary = {
    "observationID": str,
    "deploymentID": str,
    "mediaID": str,
    "eventID": str,
    "eventStart": "float32",
    "eventEnd": "float32",
    "frequencyLow": "float32",
    "frequencyHigh": "float32",
    "observationLevel": str,
    "observationType": str,
    "scientificName": str,
    "count": "Int64",           # with capital i, not int64 or Int32
    "lifeStage": str,
    "sex": str,
    "behavior": str,
    "individualID": str,
    "individualPositionRadius": "float32",
    "classificationMethod": str,
    "classifiedBy": str,
    "classificationTimestamp": str,  # datetime
    "classificationProbability": "float32",
    "observationTags": str,
    "observationComments": str
}

observations_unique_dictionary = {
    "observationID": True,
    "deploymentID": False,
    "mediaID": False,
    "eventID": False,
    "eventStart": False,
    "eventEnd": False,
    "frequencyLow": False,
    "frequencyHigh": False,
    "observationLevel": False,
    "observationType": False,
    "scientificName": False,
    "count": False,
    "lifeStage": False,
    "sex": False,
    "behavior": False,
    "individualID": False,
    "individualPositionRadius": False,
    "classificationMethod": False,
    "classifiedBy": False,
    "classificationTimestamp": False,
    "classificationProbability": False,
    "observationTags": False,
    "observationComments": False
}

observations_enum_dictionary = {
    "observationType": [
        "animal",
        "rain",
        "flowing water",
        "wind",
        "human voice",
        "electro-mechanical",
        "silence",
        "unknown",
        "unclassified"
    ],
    "classificationMethod": ["human", "machine"],
}

observations_date_columns = [
    "classificationTimestamp",
]
class Observations(CSVPamDP):
    def __init__(
        self,
        filepath: str,
        timezone,
        load_args: Dict[str, Any] | None = None,
        save_args: Dict[str, Any] | None = None,
        version: Version | None = None,
        credentials: Dict[str, Any] | None = None,
        fs_args: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ):
        super().__init__(
            pamdp_columns=observations_pamdp_columns,
            required_dictionary=observations_required_dictionary,
            schema_dictionary=observations_schema_dictionary,
            unique_dictionary=observations_unique_dictionary,
            enum_dictionary=observations_enum_dictionary,
            filepath=filepath,
            timezone=timezone,
            date_columns=observations_date_columns,
            load_args=load_args,
            save_args=save_args,
            version=version,
            credentials=credentials,
            fs_args=fs_args,
            metadata=metadata,
        )

    def _load(self):
        df = super()._load()

        return df

    def _save(self, df):
        super()._save(df)
