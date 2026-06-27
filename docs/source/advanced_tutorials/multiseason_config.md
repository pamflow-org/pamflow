## Multi‐Season Configuration

Passive acoustic monitoring projects are typically repeated over multiple seasons or years. Maintaining a reproducible analysis workflow is therefore essential. `pamflow` addresses this need by leveraging the Kedro framework, which supports season-specific configurations through environments while allowing shared settings, such as a global output path, to be defined once.

### Directory Structure

```
conf/
├── base/
│   ├── catalog.yml       ← shared catalog with ${globals:output_dir} references
│   ├── parameters.yml    ← shared default parameters
│   └── globals.yml       ← default output path (single-season projects stop here)
├── dry_2023/
│   ├── parameters.yml
│   ├── catalog.yml
│   └── globals.yml       ← overrides output_dir for this season
└── wet_2024/
    ├── parameters.yml
    ├── catalog.yml
    └── globals.yml
```

### 1. Set the Default Output Path

For projects with a single season, define the output path in `conf/base/globals.yml`:

```yaml
# conf/base/globals.yml
output_dir: data/output
```

This is enough. No season-specific files are needed and all runs write to `data/output/`.

### 2. Override per Season

For multi-season projects, create a configuration folder inside `conf/` and add a `globals.yml` to each season's configuration folder:

```yaml
# conf/dry_2023/globals.yml
output_dir: data/output_dry_2023

# conf/wet_2024/globals.yml
output_dir: data/output_wet_2024
```

### 3. Adjust Season Configuration
Here's a version that is a bit more explicit about the relationship between each season, its deployment sheet, and the corresponding Kedro configuration.

---

### 3. Configure Each Season

Each seasonal environment under `conf/` must have:

1. A **field deployment spreadsheet** describing the deployments for that season.
2. A **catalog entry** referencing that spreadsheet.
3. An **`audio_root_directory`** pointing to the root directory containing the audio recordings for that season.

For example, if your project contains the environments `dry_2023` and `wet_2023`:

#### Field deployment spreadsheet

Create one deployment spreadsheet for each season, for example:

```text
data/input/field_deployments/
├── field_deployments_sheet_dry_2023.xlsx
└── field_deployments_sheet_wet_2023.xlsx
```

#### Update the catalog

In each seasonal catalog (`conf/<season>/catalog.yml`), update the `filepath` to reference the corresponding deployment spreadsheet.

For example, in `conf/dry_2023/catalog.yml`:

```yaml
field_deployments_sheet@pandas:
  type: pamflow.datasets.pamDP.field_deployments_sheet.FieldDeployments
  filepath: data/input/field_deployments/field_deployments_sheet_dry_2023.xlsx
```

and in `conf/wet_2023/catalog.yml`:

```yaml
field_deployments_sheet@pandas:
  type: pamflow.datasets.pamDP.field_deployments_sheet.FieldDeployments
  filepath: data/input/field_deployments/field_deployments_sheet_wet_2023.xlsx
```

#### Update the audio directory

In each environment's `parameters.yml`, set the root directory containing that season's audio files.

For `conf/dry_2023/parameters.yml`:

```yaml
audio_root_directory: /data/audio_dry_2023
```

For `conf/wet_2023/parameters.yml`:

```yaml
audio_root_directory: /data/audio_wet_2023
```

The `audio_root_directory` should point to the directory containing all audio recordings associated with the corresponding field deployment spreadsheet. This ensures that each Kedro environment is fully configured to process a single monitoring season independently.

### 4. Run using environment

Single season (uses `conf/base/globals.yml`):
```bash
kedro run
```

Specific season:
```bash
kedro run --env=dry_2023
kedro run --env=wet_2024
```

Kedro merges `conf/base/` with the selected environment, with the environment values taking precedence. Each season writes to its own output folder, making reruns safe without overwriting previous results.