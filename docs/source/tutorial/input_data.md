# Input data: minimum required information for **pamflow**

In this section you will get familiar with the data collected during the project. In general, these are the input files that **pamflow** requires to work and are common among many PAM projects.

## Table of Contents
1. [Audio Root Directory](#devices-root-directory)
2. [Field deployment](#field-deployment)
3. [Target species](#target-species)


# Audio Root Directory

During the collaboration between Humboldt Institute and local communities at Guaviare, Colombia, {{number_of_sensors}} passive acoustic sensors where installed for {{number_of_days}} days. The sensors where programmed for recording one minute each 30 minutes so for each day and each installed microphone 48 files were collected for a total number of {{ number_of_wav_files}} one minute recordings. 

The resulting audio files are stored in a  external disk that's been delivered to you by  field researchers. The audios are organized as shown bellow

```
/guaviare_project_external_disk/pam_data_guaviare/
├── MC-002/    # Folder containing audio files from sensor MC-002
├── MC-009/    # Folder containing audio files from sensor MC-009
└── MC-013/    # Folder containing audio files from sensor MC-013
```

Each of the {{number_of_sensors}} subfolders corresponds to one of the installed sensors and stores the 48 one-minute audio files collected by the sensor. These are the audio files from which **pamflow** will help you extract metadata, detected species and audio segments later on the tutorial. This folder containing all the audio files per sensor is called `audio_root_directory`. 


# Field deployment

Field researchers installed the acoustic sensors and took notes on everything important regarding the installation: coordinates, dates, time, sensor characteristics and  ecological traits of the deployment site. 

These notes were handed out to you along with the recordings in a format  called `field_deployments_sheet`. This is a `.xlsx` file with one row per installed sensor having all the previously mentioned data regarding the installation of the sensor. 

# Target species

Even though there are many bird species at the monitoring site, the community is only interested in a few of them considered relevant for conservation. Along with the `devices_root_directory` and the `field_deployments_sheet`, you were given the list of relevant species for the project, namely, the `target_species`, which is a `.csv` file with only one column (`scientificName`) and one row per each one of the species considered important  for this particular project. 

| Scientific Name          |
|--------------------------|
| Amazona farinosa         |
| Cyanocorax violaceus     |
| Pitangus sulphuratus     |
| Ramphastos tucanus       |


These are the three only inputs required to run **pamflow**. Now that you understand what they are and their structure let's move on with [next section](./data_preparation.md) to learn how to input them into **pamflow**. 