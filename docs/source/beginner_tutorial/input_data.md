## Set up the data

Now that your computer has the required programms for running **pamflow** you can focus on The Guaviare Project. In this section you will download and get familiar with the data collected on the field. These input files are not only part of The Guaviare Project but are also the data that **pamflow** requires in any other passive acoustic monitoring project.

***Summary***:
```{contents}
   :depth: 1
   :local:
```

### 1. Download audio recordings
The audio recordings you'll need for this tutorial can be found on [Zenodo](https://zenodo.org/records/17148157). This sample data is provided to show you how to use pamflow. If you plan to use these recordings for other purposes, please get in touch and make sure to give proper attribution.

### 2. Audio Root Directory

During The Guaviare Project {{number_of_sensors}} passive acoustic sensors where installed for {{number_of_days}} days. The sensors where programmed for recording one minute every 30 minutes so, if everything went well, for each day and each installed sensor 48 files were collected for a total number of {{ number_of_wav_files}} one-minute recordings. 

The resulting audio files are stored in an  external disk that's been delivered to you by  field researchers. The audios are organized as shown bellow

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

Each of the {{number_of_sensors}} subfolders corresponds to one of the installed sensors and stores the {{ number_of_wav_files_per_sensor}} one-minute audio files collected by the sensor. These are the audio files from which **pamflow** will help you extract metadata, perform quality checks, detect species and extract audio segments. This folder containing all the audio files per sensor is called `audio_root_directory`. 

> **⚠️ Warning:** Ensure the file names of the audio files meets the format above.  When working with your
> own audio data, the audio files need to be named following the nomenclature: 
> {Sensor name}_{date}_{time}.WAV
> **pamflow** will ignore files named after a different structure.

### 3. Field deployment

Field researchers installed the acoustic sensors and took notes on everything important regarding the installation: coordinates of the site, date and time of installation,  sensor characteristics and  ecological traits of the deployment site. 

These notes were handed out to you along with the recordings in a format  called `field_deployments_sheet`. This is a `.xlsx` file with one row per installed sensor having all the previously mentioned data regarding the installation of the sensor. 

### 4. Target species

Even though there are many bird species at the monitoring site, the community is only interested in a few of them considered relevant for conservation. Along with the `devices_root_directory` and the `field_deployments_sheet`, you were given the list of relevant species for the project, namely, the `target_species`, which is a `.csv` file with only one column (`scientificName`) and one row per each one of the species considered important  for this particular project. 

| Scientific Name          |
|--------------------------|
| Amazona farinosa         |
| Cyanocorax violaceus     |
| Pitangus sulphuratus     |
| Ramphastos tucanus       |


These are the three only inputs required to run **pamflow**. Now that you understand what they are and their structure let's move on with [next section](./data_preparation.md) to learn how to get **pamflow** to read them. 