# Workflow structure and execution

```{toctree}
:maxdepth: 1
:caption: Workflow structure and execution
index.md
running_the_workflow.md
pipeline_details.md
```

## Overview

This workflow provides a modular Kedro-based pipeline for ecological acoustic analysis. 
It standardizes field data, performs sensor quality checks, detects species, computes acoustic indices, 
and generates graphical soundscape representations.

**Input data:**
- Audio recordings organized by deployment, see section [Input data standards](../data_standardization/data_exchange_format.md#input-data-standards).
- Field deployment sheet in `.csv` or `.xlsx` format.

**Main outputs:**
- Standardized metadata in pamDP format, see section [Output data standards](../data_standardization/data_exchange_format.md#output-data-standards).
- Acoustic indices csv files per deployment.
- Graphical soundscape csv files per deployment.

**Configuration**
All pipeline parameters are stored in the Kedro configuration folder:
- `conf/base/parameters.yml` — default parameters
- `conf/local/parameters.yml` — local overrides (ignored by Git)

You can modify these files to change processing behavior without editing code.

**Data catalog**

All datasets used by the pipelines are defined in `conf/base/catalog.yml`.

**Example:**
```yaml
media@pamDP:
  type:  pamflow.datasets.pamDP.media.Media
  filepath: data/output/data_preparation/media.csv
  timezone: Etc/GMT+5
```

Check the [Kedro documentation](https://docs.kedro.org/en/1.0.0/getting-started/kedro_concepts/) for more details.
