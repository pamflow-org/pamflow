<div align="center">
  <img src="https://github.com/pamflow/pamflow/raw/main/docs/meta/images/pamflow_logo.png" alt="pamflow logo" width="400"/>
</div>

![Python version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)

**pamflow** is a workflow for analyzing passive acoustic monitoring data using Python. It is designed to offer an easy-to-use and reproducible framework for researchers, conservation biologists, citizen scientists, and anyone interested in ecoacoustics and soundscape ecology.

## Before You Begin

### 1. Download This Repository
On the public instance of this repository, regular github cloning is available. However, the anonymized version only allows direct ownload of the repository. Hit the `Download repository` button on the upper right corner of the page. Afterwards, change to the downloaded directory
```bash
cd pamflow
```

### 2. Set Up a Working Environment
Ensure you have Python 3.11 installed. Then, create and activate a virtual environment using conda:

```bash
conda create -n pamenv python=3.11
conda activate pamenv
```

Next, install the required dependencies based on your OS. For windows run

```bash
pip install -r requirements-win.txt
```
For MacOS run
```bash
pip install -r requirements-mac.txt
```
### 3. Organize PAM Data
#### 3.1 Audio Data
All audio files must be stored in a dedicated directory. Each subdirectory within this directory should have a unique identifier corresponding to the ID or name of each sensor. This structure ensures that recordings are properly associated with their respective sensors.

To get **pamflow** to read this data follow next section's instructions. 
#### 3.2 Metadata 
Make sure you have a field deployment sheet in an Excel format. This sheet must contain a column named `recorderID`, where each value matches the names of the subdirectories in the audio data directory. This ensures proper linking between metadata and recorded audio files.

#### 3.3 Target species
For filtering out animal detections, a  custom list of species of interest can be provided to **pamflow**. It has to be a `.csv` file with a single column (`scientificName`) containing scientific names for the target species. This file is not mandatory for **pamflow** to run. If this file is not provided, **pamflow** will leave [`observations`](https://pamflow.readthedocs.io/en/latest/data_standardization/data_exchange_format.html#observations) file unchanged.

#### 3.3 Sample toy data

For an example of properly formated data or to have a sample dataset to try **pamflow**, download [pamflow's beginner tutorial dataset](https://drive.google.com/drive/folders/1L74aYdZ972R96AYnw9Fe2k4Vi3Cw7uF7).

## Getting Started

### 1. Configure Local Settings

Inside the folder `./conf/local/` create the files `./conf/local/parameters.yml` and `./conf/local/catalog.yml` as follows.

Edit the `./conf/local/parameters.yml` file to specify the path to your audio files:
```yaml
audio_root_directory: <path to your directory with audio files>
```

Edit the `./conf/local/parameters.yml` file to specify the timezone of your audios (following `Area/City` format  ):
```yaml
timezone: <prefered timezone>
```

Edit the `./conf/local/catalog.yml` file to define the path to your field deployment sheet:
```yaml
field_deployments_sheet@pandas:
  type: pandas.ExcelDataset
  filepath: <path to your Excel file with deployment information>
```
For providing a file with species of interest, edit the `./conf/local/catalog.yml` file to define the path to your target species file:

```yaml
target_species@pandas:
  type: pamflow.datasets.pamDP.target_species.TargetSpecies
  filepath: <path to your .csv file with target species>
```

It is advisable to use the subfolders inside `./data/input/` to store field deployments sheet and target species file. 
```
data/
├── input/                          # Input data and configurations
│   ├── field_deployments/          
│   ├── manual_annotations/         
│   └── target_species/             
│       └── target_species.csv # Target species list
└── output
```


### 2. Run Workflows

The workflow can be executed entirely with the command:
```bash
kedro run
```
However, for the first execution, it is recommended to run one pipeline at a time for better control.

#### 2.1. Prepare data
```bash
kedro run --pipeline=data_preparation
```

#### 2.2. Revise quality of deployments and recordings
```bash
kedro run --pipeline=quality_control
```

#### 2.3. Detect species with AI
```bash
kedro run --pipeline=species_detection
```

#### 2.4. Compute Acoustic Indices
```bash
kedro run --pipeline=acoustic_indices
```

#### 2.5. Generate Graphical Soundscapes
```bash
kedro run --pipeline=graphical_soundscape
```

### Access output data

The outputs resulting from  running  the entire workflow or individual pipelines will be inside the corresponding subfolders within `./data/output/`.
```
data/
├── input/  
└── output/ # Generated output data from pipeline runs
    ├── acoustic_indices/ 
    ├── data_preparation/ 
    ├── graphical_soundscape/ 
    ├── quality_control/
    └── species_detection/          
               
```

For more information on the outputs and its interpretation visit [Pipeline details page](https://pamflow.readthedocs.io/en/latest/documentation/pipeline_details.html) on the documentation.

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.
