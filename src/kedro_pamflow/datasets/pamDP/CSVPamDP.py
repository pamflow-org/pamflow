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




class CSVPamDP(CSVDataset):
    def __init__(self, 
    pamdp_columns,
    required_dictionary,
    schema_dictionary,
    unique_dictionary,
    filepath: str, 
    load_args: Dict[str, Any] | None = None, 
    save_args: Dict[str, Any] | None = None, 
    version: Version| None = None,
    credentials: Dict[str, Any] | None = None, 
    fs_args: Dict[str, Any] | None = None, 
    metadata: Dict[str, Any] | None = None,
    


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

        self.pamdp_columns=pamdp_columns
        self.required_dictionary=required_dictionary
        self.schema_dictionary=schema_dictionary
        self.unique_dictionary=unique_dictionary

    
    def _load(self):
        df=super()._load()
        # 1. Check column names & order
        if set(df.columns) != set(self.pamdp_columns):
            if set(df.columns).issubset( set(self.pamdp_columns)):
                raise ValueError(f"Missing columns for pamDP.Media format: \n list of missing columns {set(self.pamdp_columns)-set(df.columns)}")
            elif set(  self.pamdp_columns ).issubset(df.columns ):
                raise ValueError(f"Extra columns for pamDP.Media format: \n The following columns are not part of pamDP.Media format {set(df.columns)-set(self.pamdp_columns )}")
            else: 
                raise ValueError(f"""Column mismatch. There are extra and missing columns for pamDP.Media format. \n Expected columns: {self.pamdp_columns} 
                \n Missing columns: {set(self.pamdp_columns)-set(df.columns)} 
                \n Extra Columns{set(df.columns)-set(self.pamdp_columns )}""")

        # 2. Check column types
        try:
            df.astype(self.schema_dictionary)
        except ValueError as err:
            raise err

        # 3. Check mandatory columns for nulls
        for col, mandatory in self.required_dictionary.items():
            if df[col].isnull().any() and mandatory:
                raise ValueError(f"Mandatory column {col} contains null values.")

        # 4. Check unique constraints
        for col, unique_constraint in self.unique_dictionary.items():

            if df[col].duplicated().any() and unique_constraint:
                raise ValueError(f"Column {col} has duplicate values but should be unique.")
        
        return df[self.pamdp_columns]
    def _save(self,df):
        # 1. Check column names & order
        if set(df.columns) != set(self.pamdp_columns):
            if set(df.columns).issubset( set(self.pamdp_columns)):
                raise ValueError(f"Missing columns for pamDP.Media format: \n list of missing columns {set(self.pamdp_columns)-set(df.columns)}")
            elif set(  self.pamdp_columns ).issubset(df.columns ):
                raise ValueError(f"Extra columns for pamDP.Media format: \n The following columns are not part of pamDP.Media format {set(df.columns)-set(self.pamdp_columns )}")
            else: 
                raise ValueError(f"""Column mismatch. There are extra and missing columns for pamDP.Media format. \n Expected columns: {self.pamdp_columns} 
                \n Missing columns: {set(self.pamdp_columns)-set(df.columns)} 
                \n Extra Columns{set(df.columns)-set(self.pamdp_columns )}""")

        # 2. Check column types
        try:
            df.astype(self.schema_dictionary)
        except ValueError as err:
            raise err

        # 3. Check mandatory columns for nulls
        for col, mandatory in self.required_dictionary.items():
            if df[col].isnull().any() and mandatory:
                raise ValueError(f"Mandatory column {col} contains null values.")

        # 4. Check unique constraints
        for col, unique_constraint in self.unique_dictionary.items():

            if df[col].duplicated().any() and unique_constraint:
                raise ValueError(f"Column {col} has duplicate values but should be unique.")
        #return df[self.pamdp_columns]
        super()._save(df[self.pamdp_columns])