# Documentation

## Running the workflow

To run the entire workflow, you can use the following command

```bash
kedro run
```
However, for better control and to understand each step, it's highly recommended to run the pipelines individually, especially during your first execution.

```bash
kedro run --pipeline <pipeline_name>
```

For a finner grained execution, run individual nodes whithin a pipeline.

```bash
kedro run --nodes <nodes_names>
```

Check the full list of posibilities to run the workflow in the [kedro documentation web page](https://docs.kedro.org/en/1.0.0/getting-started/commands_reference/#kedro-run).

## Pipelines details

### 1. `data_preparation`

**Description**<br>
Reads field and audio data to standardize metadata using the pamDP standard. It outputs media and deployment formats, ensuring coherence between field sheets and collected audio files for later analysis and exchange.

**Parameters**<br>
This pipeline requires no parameters. Adjustments to the field deployment sheet structure can be set using the **Catalog** entry `field_deployments_sheet@pandas`.

**Nodes**
| Node name | Inputs | Outputs | Description |
|------------|---------|-----------|--------------|
| `get_media_file_node` | `params:audio_root_directory`<br>`field_deployments_sheet@pandas` | `media@pamDP` | Retrieves media files from the specified audio root directory and links them with field deployment sheet data. |
| `get_media_summary_node` | `media@pamDP` | `media_summary@pandas` | Generates a summary of the media files (e.g., counts, durations, metadata). |
| `field_deployments_sheet_to_deployments_node` | `field_deployments_sheet@pandas`<br>`media_summary@pandas` | `deployments@pamDP` | Converts the field deployments sheet and media summary into structured deployment data. |


### 2. quality_control

After the data is prepared, this pipeline performs a series of checks to verify the quality of your deployments and recordings, identifying any issues before moving on to analysis.

```bash
kedro run --pipeline=quality_control
```

### 3. species_detection

This pipeline utilizes AI models to automatically detect and identify species within your acoustic data.

```bash
kedro run --pipeline=species_detection
```

### 4. acoustic_indices

This step processes your audio files to calculate various acoustic indices. These indices provide a quantitative overview of the soundscape, useful for a wide range of analyses.

```bash
kedro run --pipeline=acoustic_indices
```

### 5. graphical_soundscape

This step allows to compute a representation of the most prominent spectro-temporal dynamics over a 24-hour window per each deployment.

```bash
kedro run --pipeline=graphical_soundscape
```