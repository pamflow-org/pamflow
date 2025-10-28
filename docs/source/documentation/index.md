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

## Pipeline details

### 1. Data preparation

```bash
kedro run --pipeline data_preparation
```

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


### 2. Quality control

```bash
kedro run --pipeline quality_control
```

**Description**<br>
Allows a quick data exploration to flag underperforming sensors and ensure data integrity for reliable ecological analysis. It summarizes survey effort, plotting sensor locations, and checking recording timelines.

**Nodes**
| Node name | Description | Inputs | Outputs |
|------------|--------------|---------|----------|
| `plot_sensor_performance_node` | Generates visualizations and summary data of sensor performance metrics based on media data. | `media@pamDP` | `sensor_performance_figure@matplotlib`<br>`sensor_performance_data@pandas` |
| `plot_sensor_location_node` | Creates a map or plot showing sensor deployment locations using summarized media and deployment data. | `media_summary@pandas`<br>`deployments@pamDP`<br>`params:sensor_location_plot` | `sensor_location@matplotlib` |
| `plot_survey_effort_node` | Produces a plot summarizing survey effort (e.g., recording hours or deployment durations). | `media_summary@pandas`<br>`deployments@pamDP`<br>`media@pamDP` | `survey_effort@matplotlib` |
| `get_timelapse_node` | Generates timelapse audio samples and corresponding spectrogram images for visual and acoustic analysis. | `sensor_performance_data@pandas`<br>`media@pamDP`<br>`params:timelapse.sample_length`<br>`params:timelapse.sample_period`<br>`params:timelapse.sample_date`<br>`params:timelapse_plot` | `timelapse@PartitionedAudio`<br>`timelapse_spectrograms@PartitionedImage` |

<details>

<summary>Parameters</summary>

| Group | Name | Description | Default Value |
|--------|------|--------------|----------------|
| `sensor_location_plot` | `fig_height` | Figure height (in inches) | `8` |
| `sensor_location_plot` | `fig_width` | Figure width (in inches) | `8` |
| `sensor_location_plot` | `marker_size` | Size of the location markers | `40` |
| `sensor_location_plot` | `marker_color` | Color of the location markers | `'slateblue'` |
| `sensor_location_plot` | `text_size` | Size of the text annotations (if 0 or negative, no text is shown) | `9` |
| `sensor_location_plot` | `alpha` | Transparency level of the markers | `0.7` |
| `timelapse_plot` | `fig_height` | Figure height (in inches) | `4` |
| `timelapse_plot` | `fig_width` | Figure width (in inches) | `15` |
| `timelapse_plot` | `nperseg` | Number of data points per segment | `1024` |
| `timelapse_plot` | `noverlap` | Number of overlapping points | `512` |
| `timelapse_plot` | `flims` | Frequency limits (Hz) | `[0, 24000]` |
| `timelapse_plot` | `db_range` | Dynamic range in decibels | `90` |
| `timelapse_plot` | `colormap` | Colormap options: 'grey', 'viridis', 'plasma', 'inferno', 'cividis' | `'viridis'` |
| `timelapse` | `sample_length` | Length of each sample for timelapse (in seconds) | `5` |
| `timelapse` | `sample_period` | Time interval between samples (e.g., '30min') | `'30min'` |
| `timelapse` | `sample_date` | Specific date for timelapse (YYYY-MM-DD). If null, the date with the most data will be used. | `null` |
</details>

### 3. Species detection

**Description**<br>
Automates species detection using a TensorFlow or BirdNET model. It filters observations based on target species, then saves customized audio segments for revision. All data follows pamDP standards.

```bash
kedro run --pipeline species_detection
```
**Parameters**<br>

**Nodes**

### 4. Acoustic indices

```bash
kedro run --pipeline acoustic_indices
```

**Description**<br>
Processes audio files to calculate various acoustic indices. These indices provide a quantitative overview of the soundscape, useful for a wide range of analyses.

**Parameters**<br>

**Nodes**

### 5. Graphical soundscape

```bash
kedro run --pipeline graphical_soundscape
```

**Description**<br>
Computes a representation of the most prominent spectro-temporal dynamics over a 24-hour window per each deployment.

**Parameters**<br>

**Nodes**
