# Overview

This workflow provides a modular Kedro-based pipeline for ecological acoustic analysis. 
It standardizes field data, performs sensor quality checks, detects species, computes acoustic indices, 
and generates graphical soundscape representations. An additional `detection_validation` pipeline, run separately
once expert annotations are available, estimates detection reliability per species and recommends a working
confidence threshold.

**Input data:**
- Audio recordings organized by deployment, see section [Input data standards](../data_standardization/data_exchange_format.md#input-data-standards).
- Field deployment sheet in `.csv` or `.xlsx` format.

**Main outputs:**
- Standardized metadata in pamDP format, see section [Output data standards](../data_standardization/data_exchange_format.md#output-data-standards).
- Acoustic indices csv files per deployment.
- Graphical soundscape csv files per deployment.

**Configuration**

Pipeline parameters are managed through Kedro's configuration system.

- `conf/base/parameters.yml` contains the complete set of default parameters distributed with pamflow.
- `conf/local/parameters.yml` contains project-specific overrides and is intended to be edited by the user.

Values defined in `conf/local/parameters.yml` take precedence over those defined in `conf/base/parameters.yml`. For this reason, the local configuration file typically contains only a small subset of parameters that commonly vary between projects, such as the audio directory location or time zone.

**Data catalog**

The complete dataset catalog distributed with pamflow is defined in `conf/base/catalog.yml`.

Users should normally avoid modifying this file directly. Instead, project-specific paths and settings can be provided through `conf/local/catalog.yml`, whose entries override the corresponding definitions in `conf/base/catalog.yml`.

The `conf/local/catalog.yml` file is intentionally minimal and is intended to be edited by the user to point pamflow to the appropriate input files for a particular project.
**Example:**
```yaml
media@pamDP:
  type:  pamflow.datasets.pamDP.media.Media
  filepath: data/output/data_preparation/media.csv
  timezone: Etc/GMT+5
```

Check the [Kedro documentation](https://docs.kedro.org/en/1.0.0/getting-started/kedro_concepts/) for more details.
