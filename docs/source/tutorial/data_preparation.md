## Data Preparation
Sofar, out of your assigend tasks for The Guaviare Project, you have only got familiar with the data collected by your fellow researchers. 
In this section you will learn how to get pamflow to read this data in order to standardize them and extract mor information.


***Table of Contents***: 
1. [Get **pamflow** to read input data](#get-pamflow-to-read-input-data)
2. [Extract metadata from each audio file](#extract-metadata-from-each-audio-file)
3. [Extract metadata from each sensor](#extract-metadata-from-each-sensor)


### Get **pamflow** to read input data

The first step towards using **pamflow** is to inform where the `audio_root_directory` is located. When you installed the project as explained in the [Getting started page](../contributing_guidelines.md#getting-started),  you ended up with this folder structure


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
│   ├── parameters.yml
│   └──   
└── 
```
Now open the file `conf/local/parameters.yml` and write the path to the `audio_root_directory`. The external disk provided to you is called `guaviare_project_external_disk` and inside it there is the folder we get familiar with in [previous section](./input_data.md)  called `pam_data_guaviare`. Thus, the `conf/base/parameters.yml` file should look like this now you have changed it.

```yaml
audio_root_directory: "/media/pamResearcher/guaviare_project_external_disk/pam_data_guaviare"

```

Now, for providing pamflow with your custom `field_deployments_sheet` and `target_species` go to the `data/` folder which should look like this

``` 
data/
├── input/                       # Folder containing all the input data
│   ├── field_deployments/       # Folder containing field_deployments_sheet 
│   └── target_species/          # Folder containing target_species
└── output/                      # Folder containing all outputs
```

Intuitively enough, copy `field_deployments_sheet` to the path `data\input\field_deployments_sheet\field_deployments_sheet.xlsx` and `target_species` to the path `data\input\target_species\target_species.csv`.

> **⚠️ Warning:** Ensure the `field_deployments_sheet` and `target_species` files are in the correct format.
> This means to check the files are named properly: `field_deployments_sheet.xlsx` and `target_species.csv`.
> Also make sure that the columns are properly named.

Now that your data is properly stored, you can use **pamflow** to complete your [asigned tasks](./tutorial.md)
### Extract metadata from each audio file

You already got familiar with the provided data and handed it over to *pamflow*. Now you are ready to complete your second task: Extract metadata from each audio file and each passive acoustic sensor.

Now that **pamflow** has access to your `audio_root_directory` we can ask it to read the  content of the folder and produce the `media@pamDP` table. The content of  `media@pamDP` is explained [here](../data_exchange_format.md#getting-started). The way to ask **pamflow** to produce it is by typing

```bash
kedro run --nodes get_media_file_node
```

The message

``` 
INFO     Pipeline execution completed successfully.  
```

will tell you the process is over and that now you are able to access `media@pamDP`. It will be stored in 

``` 
data/
├── input/                        # Folder containing all the input data
└── output/                       # Folder containing all outputs
    └── data_preparation/         # Folder containing outputs of the pipeline data_preparation
        └── media.csv             # `media@pamDP` file
```
 As soon as you open it you will find the following information regarding your audio files (along with other columns)

| mediaID                     | deploymentID | bboxTime | bboxDuration | Scientific Name         | classificationProbability |
|-----------------------------|--------------|----------|--------------|-------------------------|---------------------------|
| MC-013_20240302_063000.WAV  | MC-013       | 15.0     | 18.0         | Cyanocorax violaceus    | 0.192                     |
| MC-013_20240302_083000.WAV  | MC-013       | 0.0      | 3.0          | Ramphastos tucanus      | 0.666                     |
| MC-013_20240302_083000.WAV  | MC-013       | 3.0      | 6.0          | Ramphastos tucanus      | 0.615                     |
| MC-013_20240302_083000.WAV  | MC-013       | 6.0      | 9.0          | Ramphastos tucanus      | 0.871                     |
| ...                         | ...          | ...      | ...          | ...                     | ...                       |

 You can check details on the definition of each field [here](../data_exchange_format.md#getting-started).

 In the [next](./quality_control.md) section  you will learn how to check for sensor behavior and performance.