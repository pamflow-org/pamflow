## Data preparation

In the previous step you explored the three input files **pamflow** needs. Now you will configure **pamflow** to find them and run the first pipeline to extract and standardize metadata from your recordings.

### Configure audio path and timezone

Open `conf/local/parameters.yml` with any text editor (e.g. Notepad on Windows, TextEdit on macOS) and set the path to your audio folder and the timezone of your recordings. For The Guaviare Project, the recordings were made in Guaviare, Colombia, so the timezone is `America/Bogota`:

```yaml
audio_root_directory: "/media/pamResearcher/guaviare_project_external_disk/pam_data_guaviare"
timezone: "America/Bogota"
```

### Move input files to the pamflow folder

Copy the `field_deployments_sheet.xlsx` and `target_species.csv` files to their respective locations inside the pamflow folder:

- `field_deployments_sheet.xlsx` → `data/input/field_deployments/`
- `target_species.csv` → `data/input/target_species/`

### Run the data preparation pipeline

Now everything is ready to run **pamflow**'s first pipeline:

```bash
pamflow run --pipeline data_preparation
```

This pipeline generates two standardized tables stored in `data/output/data_preparation/`.

`media.csv` contains one row per audio file:

| mediaID                     | deploymentID | timestamp           | filePath                                | sampleRate | ... | bitDepth | fileLength |
|-----------------------------|--------------|---------------------|-----------------------------------------|------------|-----|----------|------------|
| MC-013_20240302_070000.WAV  | MC-013       | 2024-03-02T07:00:00 | .../MC-013/MC-013_20240302_070000.WAV   | 24000      | ... | 16       | 30.0       |
| MC-013_20240229_063000.WAV  | MC-013       | 2024-02-29T06:30:00 | .../MC-013/MC-013_20240229_063000.WAV   | 24000      | ... | 16       | 30.0       |
| MC-013_20240304_053000.WAV  | MC-013       | 2024-03-04T05:30:00 | .../MC-013/MC-013_20240304_053000.WAV   | 24000      | ... | 16       | 30.0       |

`deployments.csv` contains one row per deployment:

| deploymentID | locationID   | latitude  | longitude   | deploymentStart      | deploymentEnd        | ... | recorderModel       | habitat       |
|--------------|--------------|-----------|-------------|----------------------|----------------------|-----|---------------------|---------------|
| MC-002       | EL REBALSE   | 2.117463  | -72.779575  | 2024-02-15T15:04:45  | 2024-03-06T15:04:45  | ... | AudioMoth v 1.2.0   | Pastos limpios|
| MC-007       | SAN MIGUEL   | 2.059644  | -72.920236  | 2024-02-15T15:32:00  | 2024-03-06T15:32:00  | ... | AudioMoth v 1.2.0   | Pastos limpios|
| MC-009       | LA TORTUGA   | 2.183335  | -72.987016  | 2024-02-16T20:48:06  | 2024-03-07T20:48:06  | ... | AudioMoth v 1.2.0   | Pastos limpios|
| MC-013       | LA TORTUGA   | 2.183335  | -72.987016  | 2024-02-16T20:48:06  | 2024-03-07T20:48:06  | ... | AudioMoth v 1.2.0   | Pastos limpios|

```{seealso}
The structure and full schema of `media.csv` and `deployments.csv` are described in detail in the [Data Exchange Format](../data_standardization/data_exchange_format.md#output-data-standards) section.
```

In the [next](./quality_control.md) section you will learn how to check recorder behavior and performance.