## Detection validation

In the previous step, experts reviewed the audio segments and filled in the `positive` column of the `manual_annotations` Excel files. In this section you will use those completed annotations to run the `detection_validation` pipeline, which estimates, per species, how reliable a detection is as a function of the model's confidence score, and recommends a working threshold above which detections can be trusted.

```{tip}
Completed example annotation files for this tutorial's dataset are available for download at `TODO: insert Zenodo DOI`. If you're following along with your own data instead, use the annotation files you completed in the previous step.
```

Unlike the previous steps, `detection_validation` is not run by plain `kedro run` — it depends on the manual annotation step above, so it must be run explicitly:

```bash
pamflow run --pipeline detection_validation
```

### Validation outputs

The pipeline writes its results to `data/output/detection_validation/`.

The key output is `detection_validation_summary.csv`, with one row per species:

| Column | Description |
|---|---|
| `status` | Whether a usable threshold was found (`ok`) or, if not, why (e.g. `insufficient_sample`, `separation`, `score_not_informative`) |
| `t_star` | The recommended score threshold, when `status` is `ok` |
| `fitted_probability_at_t_star` | The estimated probability of a correct detection at that threshold |
| `n_annotated`, `n_positive`, `n_negative`, `n_uncertain` | Annotation counts backing the estimate |

A species with `status` other than `ok` doesn't yet have a reliable threshold — usually because it needs more annotations. See the [Pipeline details](../documentation/pipeline_details.md#6-detection-validation) page for the full list of statuses and what they mean.

Alongside the summary, the pipeline also writes:

- `manual_annotation_summary.csv` — annotation counts per species (including how many are still pending review)
- `plots/` — one diagnostic plot per species, showing the annotated segments, the fitted curve, and the recommended threshold
- `detection_validation_overview.pdf` — a single infographic summarizing validation status and recommended thresholds across all species

## Wrap-up

Congratulations on completing the tutorial! You have gone through the main **pamflow** workflow: from organizing and loading field data, to running quality checks on your recorders, detecting target species, preparing audio segments for expert validation, and using expert annotations to recommend a trustworthy detection threshold per species. These steps cover the core of what **pamflow** is designed to do — turning raw acoustic recordings into structured, reusable, and interpretable data.

You are now ready to run **pamflow** with your own data. Note that all pipelines can also be run node by node for greater control over each step — see the [Pipeline details](../documentation/pipeline_details.md#pipeline-details) section for a full reference, including additional pipelines such as `graphical_soundscapes` and `acoustic_indices`. If you run into any issues or have suggestions, feel free to open an issue on the [GitHub repository](https://github.com/pamflow-org/pamflow). For a deeper understanding of the data formats and outputs, refer to the [Data Exchange Formats](../data_standardization/data_exchange_format.md) section.
