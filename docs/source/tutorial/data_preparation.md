# Data Preparation

In this section you will learn how to use pamflow for data preparation and sistematization. **pamflow** uses the input data described in   [previous section](./input_data.md)  to extract the necessary metadata common to most PAM projects. 


## Table of Contents
1. [Get **pamflow** to read input data](#get-pamflow-to-read-input-data)
2. [Extract metadata from each audio file](#extract-metadata-from-each-audio-file)


## Get **pamflow** to read input data

The first step towards using **pamflow** is to inform where the `audio_root_directory` is located. When you installed the project as explained in the [Getting started page](../contributing_guidelines.md#getting-started),  you ended up with this folder structure


```plaintext
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

```plaintext
conf/
├── base/                # Base configuration files
│   ├── catalog/         # Data catalog configuration
│   ├── parameters/      # Pipeline parameters
│   ├── logging.yml      # Logging configuration
│   ├── credentials.yml  # Credentials for external services
│   └── parameters.yml   # File to inform pamflow where audio_root_directory is located
├── local/               # Local environment-specific configuration (ignored by Git)
├── catalog/             # Additional catalog configurations
├── parameters/          # Additional parameter configurations
└── credentials/         # Secure credentials (ignored by Git)
```
Now open the file `conf/base/parameters.yml` and write the path to the `audio_root_directory`. The external disk provided to you is called `guaviare_project_external_disk` and inside it there is the folder we get familiar with in [previous section](./input_data.md)  called `pam_data_guaviare`. Thus, the `conf/base/parameters.yml` file should look like this now you have changed it.

```yaml
audio_root_directory: "/media/pamResearcher/guaviare_project_external_disk/pam_data_guaviare"

```

Now, for providing pamflow with your custom `field_deployments_sheet` and `target_species`
## Extract metadata from each audio file