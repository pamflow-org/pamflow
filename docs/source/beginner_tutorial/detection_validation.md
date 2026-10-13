# Detection validation

In the previous step, experts reviewed the audio segments and filled in the `positive` column of the `manual_annotations` Excel files. In this section you will use those completed annotations to run the `detection_validation` pipeline, which estimates, per species, how reliable a detection is as a function of the model's confidence score, and recommends a working threshold above which detections can be trusted.

```{important}
The example annotation files for this tutorial's dataset are included in the [tutorial dataset](https://doi.org/10.5281/zenodo.16922848). They contain **simulated annotations, not real expert validations**, and they are provided only for teaching purposes: the results below must not be interpreted as an assessment of the actual detections. If you are following along with your own data instead, use the annotation files you completed in the previous step.
```

To follow the tutorial with the example files, copy them to `data/output/species_detection/manual_annotations/` (replacing the empty files generated in the previous step).

Unlike the previous steps, `detection_validation` is not run by plain `pamflow run` — it depends on the manual annotation step above, so it must be run explicitly:

```bash
pamflow run --pipeline detection_validation
```

## Validation outputs

The pipeline writes its results to `data/output/detection_validation/`.

The key output is `detection_validation_summary.csv`, with one row per species:

| Column | Description |
|---|---|
| `status` | Whether a usable threshold was found (`ok`) or, if not, why (e.g. `insufficient_sample`, `separation`, `score_not_informative`) |
| `t_star` | The recommended score threshold, when `status` is `ok` |
| `fitted_probability_at_t_star` | The estimated probability of a correct detection at that threshold |
| `n_annotated`, `n_positive`, `n_negative`, `n_uncertain` | Annotation counts backing the estimate |

A species with `status` other than `ok` doesn't have a reliable threshold. See the [Pipeline details](../documentation/pipeline_details.md#6-detection-validation) page for the full list of statuses and what they mean.

### Results with the example annotations

Running the pipeline on the simulated annotations gives the following summary (rounded values):

| scientificName | n_positive | n_negative | n_uncertain | status | t_star | fitted_probability_at_t_star |
|---|---|---|---|---|---|---|
| *Ara severus* | 10 | 10 | 0 | `ok` | 0.89 | 0.9 |
| *Ramphastos tucanus* | 6 | 13 | 1 | `ok` | 0.81 | 0.9 |
| *Nyctidromus albicollis* | 12 | 8 | 0 | `ok` | 0.68 | 0.9 |
| *Cyanocorax violaceus* | 7 | 12 | 1 | `ok` | 0.65 | 0.9 |
| *Amazona farinosa* | 7 | 13 | 0 | `ok` | 0.45 | 0.9 |
| *Pitangus sulphuratus* | 12 | 8 | 0 | `score_not_informative` | | |
| *Lophostrix cristata* | 0 | 20 | 0 | `insufficient_sample` | | |

How to read it:

- **Species with a threshold (`ok`).** For these species, the probability that a detection is correct increases with the confidence score. `t_star` is the lowest score at which the estimated probability reaches the target precision (`target_precision`, 0.9 by default). For example, detections of *Nyctidromus albicollis* with a score above 0.68 can be trusted, while for *Ara severus* the score must be above 0.89. Detections below the threshold should be reviewed or discarded. Note that the threshold differs among species, so a single threshold for all species would be either too permissive or too strict.
- **`score_not_informative`.** For *Pitangus sulphuratus*, correct and incorrect detections are found at all score levels, so the score does not help to separate them. The detections of this species cannot be filtered by confidence and need to be reviewed manually.
- **`insufficient_sample`.** All 20 *Lophostrix cristata* segments were marked as incorrect (and their scores are all below 0.2). This is consistent with the earlier suspicion: this forest owl is not expected in a pasture. With no correct detections there is nothing to fit, so no threshold is recommended, and this species should be discarded from the results.
- **Uncertain annotations.** Segments marked with `?` are excluded from the fit by default (`uncertain_handling: exclude`).

Alongside the summary, the pipeline also writes:

- `manual_annotation_summary.csv` — annotation counts per species (including how many are still pending review)
- `plots/` — one diagnostic plot per species, showing the annotated segments, the fitted curve, and the recommended threshold
- `detection_validation_overview.pdf` — a single infographic summarizing validation status and recommended thresholds across all species

## Wrap-up

Congratulations on completing the tutorial! You have gone through the main **pamflow** workflow: from organizing and loading field data, to running quality checks on your recorders, detecting target species, preparing audio segments for expert validation, and using expert annotations to recommend a trustworthy detection threshold per species. These steps cover the core of what **pamflow** is designed to do — turning raw acoustic recordings into structured, reusable, and interpretable data.

You are now ready to run **pamflow** with your own data. Note that all pipelines can also be run node by node for greater control over each step — see the [Pipeline details](../documentation/pipeline_details.md#pipeline-details) section for a full reference, including additional pipelines such as `graphical_soundscape` and `acoustic_indices`. If you run into any issues or have suggestions, feel free to open an issue on the [GitHub repository](https://github.com/pamflow-org/pamflow). For a deeper understanding of the data formats and outputs, refer to the [Data Exchange Formats](../data_standardization/data_exchange_format.md) section.
