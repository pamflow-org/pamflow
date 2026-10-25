# Plan: new validated_annotations schema (detection_validation + species_detection)

Status: code and tests done (202 passing in `src/tests/pipelines`); docs pending (see bottom).

## Context
`validated_annotations.csv` is built by `compile_manual_annotations` from xlsx sheets written by `create_manual_annotation_formats` (species_detection). Target schema:
`observationID, classifiedBy, scientificNameModel, classificationProbability, classificationTimestamp, category, scientificNameValidated, favorite`.
(No separate `manual_annotation` pipeline exists; it is two nodes in species_detection.)

Decisions: classifiedBy = model (from segments.csv); the sheet column formerly `positive` is now `category` (first planned as `label`, renamed because it is clearer); observationID unchanged; `classificationProbability` keeps its spelling (`classifiactionProbability` was a typo).

## Final design (implemented)
- **Annotation sheet** columns: `observationID, segmentsFilePath, filePath, classifiedBy, classificationProbability, eventStart, eventEnd, scientificNameModel, category, scientificNameValidated, favorite`, with `classificationProbability` followed by `classificationTimestamp`. `classifiedBy` and `classificationTimestamp` are prefilled from `segments` (the model's values); the annotator updates them when completing the row and the compile node passes them to `validated_annotations.csv`. `category`, `scientificNameValidated` and `favorite` are blank for the reviewer. Dropped: `detectedSpecies` and the blank human `classifiedBy`. `scientificName` is renamed only inside the sheet; observations/segments/plots are untouched.
- **category** (output): `Positive, Negative, Uncertain, Reassigned, Multitaxa`. Reviewer input is mapped through the param lists `positive_values`, `negative_values`, `uncertain_values`, `reassigned_values`, `multitaxa_values` (case-insensitive; overlaps raise `ValueError`; unrecognized values raise).
- **scientificNameValidated**:
  - Positive → model's name.
  - Negative → blank.
  - Uncertain → blank.
  - Reassigned → one species different from the model's.
  - Multitaxa → two or more species separated by `|` (param `taxa_separator`; commas are rejected).
- **Auto-promotion** when the reviewer types names that contradict the category:
  - Negative/Uncertain + one different species → Reassigned.
  - Negative/Uncertain + two or more species → Multitaxa.
  - Positive + extra species → Multitaxa, with the model's name kept first (`Sp a|Sp b`, no duplicates).
  - A name equal to the model's, or no name, leaves the category unchanged.
- **Validation errors**: Reassigned needs exactly one species different from the model's; Multitaxa needs at least two. An empty category with a filled name is treated as pending, with a warning.
- **favorite**: boolean, TRUE when the cell is in `positive_values`.
- **uncertain_handling** (exclude/positive/negative) acts on Uncertain only. Reassigned and Multitaxa are always excluded from the precision fit.
- **Fit/plots**: use rows with category Positive/Negative, keyed on `scientificNameModel`. Fit, threshold and summary outputs keep the column name `scientificName`.
- **manual_annotation_summary.csv**: per `scientificNameModel`, adds `n_reassigned` and `n_multitaxa`.
- **Legacy sheets**: `positive`, `label`, `scientificName`, `detectedSpecies` are renamed on read with a warning.

## Files changed
- `src/pamflow/pipelines/species_detection/nodes.py` — `create_manual_annotation_formats`.
- `src/pamflow/pipelines/detection_validation/nodes.py` — `compile_manual_annotations` (rewritten), `_fit_one_species`, `fit_precision_models`, `_plot_one_species`, `plot_precision_models`.
- `src/pamflow/pipelines/detection_validation/pipeline.py` — compile node gets `reassigned_values`, `multitaxa_values`, `taxa_separator`.
- `conf/base/parameters/detection_validation.yml` — the three new params.
- Tests: new `src/tests/pipelines/detection_validation/` (compile + fit); sheet-column test added to `src/tests/pipelines/species_detection/test_node_create_manual_annotation_formats.py`.

## Verified
- `pytest src/tests/pipelines`: 202 passed.
- `kedro run --pipeline detection_validation` on the sample data (Amazona farinosa etc.): runs end-to-end and writes the new columns; the legacy `label` column in the existing sheets was renamed on read.

## Pending
- **Docs not updated** (deliberately out of scope so far; they still describe `positive` / `detectedSpecies`): `docs/source/beginner_tutorial/species_detection.md` (l.53-74, example table l.65; "two columns" wording), `docs/source/documentation/pipeline_details.md` (l.102-131, 225-263 + params), `docs/source/beginner_tutorial/detection_validation.md` (add `validated_annotations` column list), `README.md` (l.57, 131), `notes/validation_pipeline_plan.md` (l.117, 135-159, 305, 315), optionally `docs/source/data_standardization/data_exchange_format.md`.
- **classifiedBy in the sample output** shows a reviewer name (`Juan Ulloa`), not `Birdnet 2.4`: the edited sheets carry a reviewer name in that column. Decide whether the sheet should prefill and lock it, or add a separate reviewer column.
- **"Multilabel"**: the Positive-plus-other-species case was implemented as `Multitaxa`. Confirm no sixth category is wanted.
- **Not covered by tests**: end-to-end `species_detection` → xlsx → `detection_validation` on fresh data (only the sheet columns and the compile/fit nodes are unit-tested); plot node and `recommend_thresholds` with the new schema have no dedicated tests.
- Existing `data/output` sheets still hold the old `label` column; regenerate them with `species_detection` to get `category`.
