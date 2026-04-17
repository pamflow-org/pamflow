## The tutorial data

Before running any analysis, you need to gather the three files that **pamflow** requires. In this section you will download the tutorial data and get familiar with its structure.

### 1. Download tutorial data
The audio recordings you'll need for this tutorial can be found [here](https://drive.google.com/drive/folders/1L74aYdZ972R96AYnw9Fe2k4Vi3Cw7uF7). 

```{note}
This sample data is provided to show you how to use pamflow, if you plan to use these recordings for other purposes, please get in touch and make sure to give proper attribution.
```

### 2. Audio recordings

During The Guaviare Project, {{number_of_sensors}} recorders were deployed for {{number_of_days}} days, programmed to record 30 seconds every 30 minutes. If everything went as expected, each deployment collected 48 files per day, for a total of {{number_of_wav_files}} one-minute recordings.

Inside the main folder `pam_data_guaviare/` you will find one subfolder per deployment, named after its deployment ID and containing all the audio files collected at that location:

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

This main folder is referred to as the `audio_root_directory` — you will use this name when configuring **pamflow** in the next step.

```{important}
   Audio file names must follow this format: `DEPLOYMENTID_DATE_TIME.WAV`
   **pamflow** will ignore any files that do not match this structure.
```

### 3. Field deployments sheet

Field researchers installed the recorders and noted key information about each deployment: site coordinates, installation date and time, recorder settings, and habitat characteristics.

These notes were handed to you alongside the recordings as the `field_deployments_sheet` — a `.xlsx` file with one row per recorder containing the above information.

### 4. Target species list

Even though the monitoring site hosts many bird species, the community is only interested in a few considered relevant for conservation. Along with the `audio_root_directory` and the `field_deployments_sheet`, you were given a list of these species: the `target_species` file, a `.csv` with a single column (`scientificName`) and one row per species.

<div style="max-width: 300px;">

| scientificName          |
|--------------------------|
| Amazona farinosa         |
| Cyanocorax violaceus     |
| Pitangus sulphuratus     |
| Ramphastos tucanus       |

</div>

```{tip}
These three files — the audio folder, the field deployments sheet, and the target species list — are all that **pamflow** needs to run. The target species file is the only optional one; if left empty, detections will not be filtered by species.
```

Now that you understand the data and its structure, let's move on to the [next step](./data_preparation.md) to load it into **pamflow**.