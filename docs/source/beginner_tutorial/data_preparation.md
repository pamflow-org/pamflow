## Data Preparation
So far, out of your assigend tasks for The Guaviare Project, you have only got familiar with the data collected by your fellow researchers. 
In this section you will learn how to get **pamflow** to read this data in order to standardize them and extract more information.

***Summary***:
```{contents}
   :depth: 1
   :local:
```

### Get **pamflow** to read input data

The first step towards using **pamflow** is to inform where the `audio_root_directory` is located. When you installed the project as explained in the [Setup page](./setup.md),  you ended up with this folder structure


``` 
kedroPamflow/
├── conf/                # Configuration files (catalog, parameters, etc.)
├── data/                # Data directory (raw, intermediate, processed, etc.)
├── docs/                # Documentation files
├── logs/                # Logs generated during pipeline runs
├── notebooks/           # Jupyter notebooks for exploration and prototyping
├── src/                 # Source code for the project
│   ├── kedroPamflow/    # Main package containing pipelines and utilities
│   └── tests/           # Unit and integration tests
├── .gitignore           # Git ignore file
├── [README.md](http://_vscodecontentref_/0)            # Project overview and setup instructions
├── requirements.txt     # Python dependencies
└── setup.py             # Installation script for the project
```


To hand your input files over  to **pamflow** you will only need two out of these folders, namely, `data/` and `conf/`. Let's focus on `conf/` first for informing **pamflow** specifically about your `audio_root_directory` . Inside `conf/` you will find this folder structure:

``` 
conf/
├── local/               
└── 
```
Inside `conf/local/` create two files:  `conf/local/parameters.yml` and `conf/local/catalog.yml`. On `conf/local/parameters.yml` write the path to the `audio_root_directory`. The external disk provided to you is called `guaviare_project_external_disk` and inside it there is the folder we get familiar with in [previous section](./input_data.md)  called `pam_data_guaviare`. 


On `conf/local/parameters.yml` you will also have to indicate the timezone of you audio files. In our case they were recorded at Guaviare, Colombia and thus the corresponding time zone is `America/Bogota`. Thus, the `conf/local/parameters.yml` file should look like this now you have changed it.

```yaml
audio_root_directory: "/media/pamResearcher/guaviare_project_external_disk/pam_data_guaviare"
timezone: "America/Bogota"

```

Now, for providing pamflow with your custom `field_deployments_sheet` and `target_species` edit the `./conf/local/catalog.yml` file as follows
```yaml
field_deployments_sheet@pandas:
  type: pandas.ExcelDataset
  filepath: <path to your Excel file with deployment information>

target_species@pandas:
  type: pamflow.datasets.pamDP.target_species.TargetSpecies
  filepath: <path to your .csv file with target species>
```



Now that your data is properly stored, you can use **pamflow** to complete your [asigned tasks](./tutorial.md)


### Standardized metadata from each audio and each sensor

You already got familiar with the provided data and handed it over to **pamflow**. Now you are ready to complete your second task: Extract metadata from each audio file and each passive acoustic sensor.

Now that **pamflow** has access to the `audio_root_directory` and `field_deployments_sheet`, we can ask it to generate the `media@pamDP` and `deployments@pamDP` formats. The former is a `.csv` containing one row per each  `.WAV` file in the `audio_root_directory` and displaying important information related to each audio. The latter, contains information about each deployed sensor. The content, schema and structure of these datasets is further explained in the [Data Exchange Formats ](../data_exchange_format.md#Observations)  section. These formats are the baseline for the rest of the processess carried out through **pamflow**.



 For generating them,  run 

```bash
kedro run --pipeline data_preparation
```

The message

``` 
INFO     Pipeline execution completed successfully.  
```

will tell you the process is over and that now you are able to access `media@pamDP` and `deployments@pamDP`. They will be stored in 

``` 
data/
├── input/                        # Folder containing all the input data
└── output/                       # Folder containing all outputs
    └── data_preparation/         # Folder containing outputs of the pipeline data_preparation
        └── media.csv             # `media@pamDP` file
        └── deployments.csv       # `deployments@pamDP` file
```
 As soon as you open `media@pamDP` you will find the following information regarding your audio files (along with other columns)

| mediaID                     | deploymentID | timestamp           | filePath                                | sampleRate | ... | bitDepth | fileLength |
|-----------------------------|--------------|---------------------|-----------------------------------------|------------|-----|----------|------------|
| MC-013_20240302_070000.WAV  | MC-013       | 2024-03-02T07:00:00 | .../MC-013/MC-013_20240302_070000.WAV   | 48000      | ... | 16       | 60.0       |
| MC-013_20240229_063000.WAV  | MC-013       | 2024-02-29T06:30:00 | .../MC-013/MC-013_20240229_063000.WAV   | 48000      | ... | 16       | 60.0       |
| MC-013_20240304_053000.WAV  | MC-013       | 2024-03-04T05:30:00 | .../MC-013/MC-013_20240304_053000.WAV   | 48000      | ... | 16       | 60.0       |

As for `deployments@pamDP` you'll find a file that looks like this 

| deploymentID | locationID   | latitude  | longitude   | deploymentStart      | deploymentEnd        | ... | recorderModel       | habitat       |
|--------------|--------------|-----------|-------------|----------------------|----------------------|-----|---------------------|---------------|
| MC-002       | EL REBALSE   | 2.117463  | -72.779575  | 2024-02-15T15:04:45  | 2024-03-06T15:04:45  | ... | AudioMoth v 1.2.0   | Pastos limpios|
| MC-007       | SAN MIGUEL   | 2.059644  | -72.920236  | 2024-02-15T15:32:00  | 2024-03-06T15:32:00  | ... | AudioMoth v 1.2.0   | Pastos limpios|
| MC-009       | LA TORTUGA   | 2.183335  | -72.987016  | 2024-02-16T20:48:06  | 2024-03-07T20:48:06  | ... | AudioMoth v 1.2.0   | Pastos limpios|
| MC-013       | LA TORTUGA   | 2.183335  | -72.987016  | 2024-02-16T20:48:06  | 2024-03-07T20:48:06  | ... | AudioMoth v 1.2.0   | Pastos limpios|


 In the [next](./quality_control.md) section  you will learn how to check for sensor behavior and performance.