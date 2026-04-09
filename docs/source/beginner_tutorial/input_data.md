## Set up the data

In this section you will download and explore the data collected in the field. These files are the inputs that **pamflow** requires for any passive acoustic monitoring project.

### 1. Download tutorial data
The audio recordings you'll need for this tutorial can be found [here](https://drive.google.com/drive/folders/1L74aYdZ972R96AYnw9Fe2k4Vi3Cw7uF7). 

Note: This sample data is provided to show you how to use pamflow, if you plan to use these recordings for other purposes, please get in touch and make sure to give proper attribution.

### 2. Configure audio path and timezone

During The Guaviare Project, {{number_of_sensors}} passive acoustic recorders were installed for {{number_of_days}} days. The recorders were programmed to record one minute every 30 minutes, so if everything went as expected, each recorder collected 48 files per day, for a total of {{number_of_wav_files}} one-minute recordings.

The audio recordings are organized as follows:

```
/guaviare_project_external_disk/pam_data_guaviare/
├── MC-002/
│   ├── MC-002_20240229_000000.WAV
│   ├── MC-002_20240229_003000.WAV
│   ├── MC-002_20240229_010000.WAV
│   ├── MC-002_20240229_013000.WAV
│   └── MC-002_20240229_020000.WAV
├── MC-007/ 
├── MC-009/  
└── MC-013/  
```

Each of the {{number_of_sensors}} subfolders corresponds to one recorder and contains {{number_of_wav_files_per_sensor}} one-minute audio files. This folder is referred to as the `audio_root_directory`.

.. warning::

   Audio file names must follow this format: `DEPLOYMENTID_DATE_TIME.WAV`
   **pamflow** will ignore any files that do not match this structure.


### 3. Field deployment

Field researchers installed the recorders and noted key information about each deployment: site coordinates, installation date and time, recorder settings, and habitat characteristics.

These notes were handed to you alongside the recordings as the `field_deployments_sheet` — a `.xlsx` file with one row per recorder containing the above information.

### Move input files to the pamflow folder

Copy the `field_deployments_sheet.xlsx` and `target_species.csv` files to their respective locations inside the pamflow folder:

- `field_deployments_sheet.xlsx` → `data/input/field_deployments/`
- `target_species.csv` → `data/input/target_species/`


This sheet must meet the requirements listed in [Input data standards](../data_standardization/data_exchange_format.md#field-deployment-sheet). Importantly, the `deploymentID` column values must match the subfolder names in the `audio_root_directory`, so that **pamflow** can correctly link metadata to audio files.

### 4. Target species

Even though the monitoring site hosts many bird species, the community is only interested in a few considered relevant for conservation. Along with the `audio_root_directory` and the `field_deployments_sheet`, you were given a list of these species: the `target_species` file, a `.csv` with a single column (`scientificName`) and one row per species.

| Scientific Name          |
|--------------------------|
| Amazona farinosa         |
| Cyanocorax violaceus     |
| Pitangus sulphuratus     |
| Ramphastos tucanus       |

.. note::
   
   These are the three only inputs required to run **pamflow**. Now that you understand what they are and their structure let's move on with [next section](./data_preparation.md) to learn how to get **pamflow** to read them. 
