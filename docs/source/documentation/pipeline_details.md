# Pipeline details

## 1. Data preparation

```bash
pamflow run --pipeline data_preparation
```

**Description**<br>
Reads field and audio data to standardize metadata using the pamDP standard. It outputs media and deployment formats, ensuring coherence between field sheets and collected audio files for later analysis and exchange.

**Parameters**<br>
This pipeline requires no parameters. Adjustments to the field deployment sheet structure can be set using the **Catalog** entry `field_deployments_sheet@pandas`.

**Nodes**
| Node name | Description | Inputs | Outputs |
|------------|--------------|---------|----------|
| `get_media_file_node` | Retrieves media files from the specified audio root directory and links them with field deployment sheet data. | `params:audio_root_directory`<br>`field_deployments_sheet@pandas` | `media@pamDP` |
| `get_media_summary_node` | Generates a summary of the media files (e.g., counts, durations, metadata). | `media@pamDP` | `media_summary@pandas` |
| `field_deployments_sheet_to_deployments_node` | Converts the field deployments sheet and media summary into structured deployment data. | `field_deployments_sheet@pandas`<br>`media_summary@pandas` | `deployments@pamDP` |

## 2. Quality control

```bash
pamflow run --pipeline quality_control
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
<br>

## 3. Species detection

**Description**<br>
Automates species detection using a TensorFlow or BirdNET model. It filters observations based on target species, then saves customized audio segments for revision. All data follows pamDP standards.

```bash
pamflow run --pipeline species_detection
```
**Nodes**
| Node name | Description | Inputs | Outputs |
|------------|--------------|---------|----------|
| `species_detection_node` | Runs the species detection algorithm in parallel using media and deployment data to generate unfiltered species observations. | `media@pamDP`<br>`deployments@pamDP`<br>`params:species_detection_parameters.n_jobs` | `unfiltered_observations@pamDP` |
| `filter_observations_node` | Filters unfiltered observations based on target species, minimum number of observations, and segment size parameters. | `unfiltered_observations@pamDP`<br>`target_species@pandas`<br>`params:species_detection_parameters.minimum_observations`<br>`params:species_detection_parameters.segment_size` | `observations@pamDP` |
| `create_segments_node` | Creates time or frequency segments from observations and associated media based on segment size. | `observations@pamDP`<br>`media@pamDP`<br>`params:species_detection_parameters.segment_size` | `segments@pandas` |
| `create_segments_folder_node` | Generates an audio folder dataset from created segments for downstream processing or manual validation. | `segments@pandas`<br>`params:species_detection_parameters.n_jobs`<br>`params:species_detection_parameters.segment_size` | `segments_audio_folder@AudioFolderDataset` |
| `create_manual_annotation_formats_node` | Produces manual annotation files from segment data for human validation or annotation tools. | `segments@pandas`<br>`params:species_detection_parameters.manual_annotations_file_name` | `manual_annotations@PartitionedDataset` |
| `plot_observations_summary_node` | Creates summary plots visualizing total and temporal patterns of species observations relative to media data. | `observations@pamDP`<br>`media@pamDP` | `observations_summary@matplotlib` |
| `plot_observations_per_species_node` | Plots the number or distribution of observations per species to visualize detection results. | `observations@pamDP` | `observations_per_species@matplotlib` |

<details>
<summary>Parameters</summary>

| Group | Name | Description | Default Value |
|--------|------|--------------|----------------|
| `species_detection_parameters` | `n_jobs` | Number of cores used in parallelization. `-1` forces the use of all available cores. | `-1` |
| `species_detection_parameters` | `minimum_observations` | Minimum number of detections required for a species to be included in the observations format. | `20` |
| `species_detection_parameters` | `segment_size` | Maximum number of sample segments generated per species (fewer are used if a species has fewer available observations). | `20` |
| `species_detection_parameters` | `manual_annotations_file_name` | Prefix for manual annotation files, formatted as `{manual_annotations_file_name}_{species}`. | `'species_manual_annotations'` |

</details>
<br>


## 4. Acoustic indices

```bash
pamflow run --pipeline acoustic_indices
```

**Description**<br>
Processes audio files to calculate various acoustic indices. These indices provide a quantitative overview of the soundscape, useful for a wide range of analyses.

**Nodes**
| Node name | Description | Inputs | Outputs |
|------------|--------------|---------|----------|
| `compute_indices_node` | Computes acoustic indices from media data based on provided parameters, generating partitioned datasets for further ecological or acoustic analysis. | `media@pamDP`<br>`params:acoustic_indices` | `acoustic_indices@PartitionedDataset` |

<details>
<summary>Parameters</summary>

| Group | Name | Description | Default Value |
|--------|------|--------------|----------------|
| `acoustic_indices.preprocess` | `nperseg` | Length of each segment for FFT during preprocessing. | `1024` |
| `acoustic_indices.preprocess` | `noverlap` | Number of points to overlap between FFT segments. | `0` |
| `acoustic_indices.preprocess` | `target_fs` | Sampling rate for acoustic index analysis. | `48000` |
| `acoustic_indices.preprocess` | `filter_type` | Type of filter applied to the audio signal (e.g., bandpass). | `bandpass` |
| `acoustic_indices.preprocess` | `filter_cut` | Frequency cutoff range for the filter in Hz. | `[300, 16000]` |
| `acoustic_indices.preprocess` | `filter_order` | Filter order defining the steepness of the filter roll-off. | `3` |
| `acoustic_indices.indices_settings.ACI` | — | Acoustic Complexity Index (no additional parameters). | — |
| `acoustic_indices.indices_settings.ADI` | `fmin` | Minimum frequency (Hz) for index calculation. | `0` |
| `acoustic_indices.indices_settings.ADI` | `fmax` | Maximum frequency (Hz) for index calculation. | `24000` |
| `acoustic_indices.indices_settings.ADI` | `bin_step` | Frequency bin width (Hz) used in analysis. | `1000` |
| `acoustic_indices.indices_settings.ADI` | `index` | Diversity index type used (e.g., shannon). | `shannon` |
| `acoustic_indices.indices_settings.ADI` | `dB_threshold` | Threshold level (in dB) for inclusion in the index computation. | `-40` |
| `acoustic_indices.indices_settings.BI` | `flim` | Frequency range (Hz) for BI index computation. | `[2000, 11000]` |
| `acoustic_indices.indices_settings.Hf` | — | Spectral entropy in the frequency domain (no parameters). | — |
| `acoustic_indices.indices_settings.Ht` | — | Temporal entropy index (no parameters). | — |
| `acoustic_indices.indices_settings.H` | — | Overall acoustic entropy combining temporal and spectral dimensions (no parameters). | — |
| `acoustic_indices.indices_settings.NDSI` | `flim_bioPh` | Frequency range (Hz) for biophony band. | `[2000, 20000]` |
| `acoustic_indices.indices_settings.NDSI` | `flim_antroPh` | Frequency range (Hz) for anthrophony band. | `[0, 2000]` |
| `acoustic_indices.indices_settings.NP` | `mode` | Peak detection mode used (e.g., linear). | `linear` |
| `acoustic_indices.indices_settings.NP` | `min_peak_val` | Minimum amplitude threshold for peaks. | `0` |
| `acoustic_indices.indices_settings.NP` | `min_freq_dist` | Minimum frequency distance (Hz) between detected peaks. | `100` |
| `acoustic_indices.indices_settings.NP` | `slopes` | Slope values for spectral peak analysis (if applicable). | `null` |
| `acoustic_indices.indices_settings.NP` | `prominence` | Minimum prominence value for peak detection. | `1e-6` |
| `acoustic_indices.indices_settings.RMS` | — | Root Mean Square energy index (no parameters). | — |
| `acoustic_indices.indices_settings.SC` | `dB_threshold` | Threshold level (in dB) for spectral cover index computation. | `-70` |
| `acoustic_indices.indices_settings.SC` | `flim_LF` | Frequency range (Hz) for low-frequency band. | `[1000, 20000]` |
| `acoustic_indices.execution` | `n_jobs` | Number of CPU cores used for parallel processing. `-1` uses all available cores. | `-1` |
</details>
<br>


## 5. Graphical soundscape

```bash
pamflow run --pipeline graphical_soundscape
```

**Description**<br>
Computes a representation of the most prominent spectro-temporal dynamics over a 24-hour window per each deployment.

**Nodes**
| Node name | Description | Inputs | Outputs |
|------------|--------------|---------|----------|
| `graphical_soundscape_node` | Generates graphical representations of the soundscape using media data and visualization parameters, producing both data outputs and image plots for analysis. | `media@pamDP`<br>`params:graphical_soundscape_parameters` | `graphical_soundscape@PartitionedDataset`<br>`graph_plot@PartitionedImage` |

<details>
<summary>Parameters</summary>

| Group | Name | Description | Default Value |
|--------|------|--------------|----------------|
| `graphical_soundscape_parameters` | `target_fs` | Target sampling frequency used when processing audio data. | `48000` |
| `graphical_soundscape_parameters` | `nperseg` | Window size used to compute the spectrogram. | `256` |
| `graphical_soundscape_parameters` | `noverlap` | Overlap between consecutive windows in the spectrogram computation. | `0` |
| `graphical_soundscape_parameters` | `db_range` | Dynamic range in decibels for spectrogram visualization. | `80` |
| `graphical_soundscape_parameters` | `min_distance` | Minimum distance between detected peaks in the spectrogram. | `5` |
| `graphical_soundscape_parameters` | `threshold_abs` | Absolute threshold (in dB) for peak detection. | `-55` |
| `graphical_soundscape_parameters` | `n_jobs` | Number of CPU cores used for parallelization. `-1` uses all available cores. | `-1` |

</details>
<br>

## 6. Detection validation

```bash
pamflow run --pipeline detection_validation
```

**Description**<br>
Estimates, per species, the probability that a detection is correct as a function of the model's confidence score, using manually annotated audio segments. It fits a logistic regression (`positive ~ classificationProbability`) per species and derives a recommended working threshold — the score above which detections meet a target precision — along with a diagnostic of whether enough annotations exist to trust that threshold.

```{note}
Unlike the other pipelines, `detection_validation` is **not** part of the default `kedro run` flow. It depends on a manual step: the `manual_annotations` `.xlsx` files produced by `species_detection` must first be reviewed and have their `positive` column filled in by an expert. Once that's done, run this pipeline explicitly with the command above.
```

**Nodes**
| Node name | Description | Inputs | Outputs |
|------------|--------------|---------|----------|
| `compile_manual_annotations_node` | Concatenates all per-species manual annotation files, normalizes the free-text `positive` column into positive/negative/uncertain categories, and applies the configured handling for uncertain annotations. | `manual_annotations@PartitionedDataset`<br>`params:detection_validation_parameters.positive_values`<br>`params:detection_validation_parameters.negative_values`<br>`params:detection_validation_parameters.uncertain_values`<br>`params:detection_validation_parameters.uncertain_handling` | `validated_annotations@pandas`<br>`manual_annotation_summary@pandas` |
| `fit_precision_models_node` | Fits a per-species logistic regression of detection correctness against classification score, flagging species with insufficient sample size or perfect separation instead of fitting. | `validated_annotations@pandas`<br>`params:detection_validation_parameters`<br>`manual_annotation_summary@pandas` | `precision_model_fits@pandas`<br>`precision_curves@pandas` |
| `recommend_thresholds_node` | Inverts each fitted curve to compute the score threshold that meets the target precision, and assigns a validity status per species. | `precision_model_fits@pandas`<br>`params:detection_validation_parameters.target_precision`<br>`params:detection_validation_parameters.significance_level`<br>`params:detection_validation_parameters.score_transform` | `detection_validation_summary@pandas` |
| `plot_precision_models_node` | Generates one diagnostic plot per species showing the annotated segments, fitted curve, confidence band, and recommended threshold. | `validated_annotations@pandas`<br>`precision_curves@pandas`<br>`detection_validation_summary@pandas`<br>`precision_model_fits@pandas` | `detection_validation_plots@PartitionedDataset` |
| `plot_validation_overview_node` | Produces a summary infographic across all species: annotation counts, validity status breakdown, and recommended thresholds. | `detection_validation_summary@pandas` | `detection_validation_overview@matplotlib` |

The key output, `detection_validation_summary.csv`, reports a `status` per species that determines whether the recommended threshold (`t_star`) can be trusted:

| Status | Meaning |
|---|---|
| `ok` | A valid threshold was found; `t_star` is usable. |
| `insufficient_sample` | Too few annotations (or too few per class) to fit a model. |
| `separation` | Scores perfectly separate positives from negatives; the fit is degenerate. |
| `score_not_informative` | The fitted relationship is not statistically significant (likelihood-ratio test). |
| `negative_slope` | Higher scores are associated with *lower* correctness probability. |
| `target_unreachable` | No observed score reaches the target precision. |
| `target_always_met` | Even the lowest observed score already meets the target precision. |

<details>
<summary>Parameters</summary>

| Group | Name | Description | Default Value |
|--------|------|--------------|----------------|
| `detection_validation_parameters` | `target_precision` | Minimum desired probability that a detection at the recommended threshold is correct. | `0.9` |
| `detection_validation_parameters` | `significance_level` | Significance threshold for the likelihood-ratio test (fitted model vs. intercept-only null model). | `0.05` |
| `detection_validation_parameters` | `confidence_level` | Confidence level used for the coefficient and plotted confidence band. | `0.95` |
| `detection_validation_parameters` | `min_annotations` | Minimum number of annotations required to attempt a fit for a species. | `15` |
| `detection_validation_parameters` | `min_per_class` | Minimum number of positive and of negative annotations required to attempt a fit. | `3` |
| `detection_validation_parameters` | `score_transform` | Transform applied to the score before fitting: `identity` or `logit`. | `'identity'` |
| `detection_validation_parameters` | `uncertain_handling` | How `uncertain` annotations are treated: `exclude`, `positive`, or `negative`. | `'exclude'` |
| `detection_validation_parameters` | `positive_values` | Recognized free-text values (case-insensitive) treated as a positive annotation. | `["1", "x", "y", "yes", "si", "sí", "true", "verdadero", "p"]` |
| `detection_validation_parameters` | `negative_values` | Recognized free-text values (case-insensitive) treated as a negative annotation. | `["0", "n", "no", "false", "falso"]` |
| `detection_validation_parameters` | `uncertain_values` | Recognized free-text values (case-insensitive) treated as an uncertain annotation. | `["?", "d", "dudoso", "uncertain"]` |

</details>
<br>