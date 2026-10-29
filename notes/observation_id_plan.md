# Plan: deterministic observationID in species_detection

## Context
Today `observationID` is the integer index of a DataFrame built in `as_completed` order (`species_detection/nodes.py:154`), so it changes between runs and projects. Replace it with a deterministic hash of (media, start_ms, end_ms, origin observer, origin label) with prefix "o". Scope now: ONLY create the ID when `unfiltered_observations` is generated. Out of scope (but must stay compatible): integration of human validations, score thresholds.

## Agreed decisions
1. Replace the integer ID with the hash (repo data is test data and gets regenerated).
2. `classifiedBy` changes from `"Birdnet 2.4"` to `"birdnet-2.4"` (`species_detection/utils.py:78`).
3. Manually added rows: option (b), kept out of `unfiltered_observations`; audited later by recomputing the ID.
4. No validation-integration node now. 5. No thresholds. 6. Up to ~350k rows per project.
7. All code in English (identifiers, comments, docstrings, logs, CLI); record this rule in a new CLAUDE.md.

## Step 1 - Soundness review (conclusions)
- Scale: 350k rows ~0.4 s of hashing (measured 1M in 1.1 s); collision probability ~ n^2/2^65 = 3e-9. No vectorization needed.
- Legit collision only if the model emits two rows with same media, times and label; not expected. The node fails listing offending rows.
- Future compatibility: `filter_observations` already keeps IDs; validations will join on `observationID`; manual rows get an ID from (media, start, end, person, species). `CSVPamDP._save` already enforces the camtrapDP column set, so no extra columns.
- `observationID` is `str` and unique in the schema; hashes fit. Existing xlsx and `validated_annotations.csv` become invalid (test data; regenerate).
- float32 and times: `eventStart/eventEnd` are stored as float32 (~7 significant digits). 12.3 s reads back as 12.30000019, and `round(x*1000)` still gives 12300, so it is safe. float32 only resolves milliseconds below ~16,777 s (~4.6 h); beyond that, the ms value would differ before vs after saving. Rule: compute the ID ONCE in the node from the float64 values BirdNET returns, before any float32 cast, and never recompute it from the CSV. The function does `round(float(x)*1000)`; a test pins the float32 case.

## Step 2 - Pure function
- New `src/pamflow/pipelines/species_detection/identifiers.py`, no Kedro dependency.
- `observation_id(media_id, start_s, end_s, origin_observer, origin_label, n_bytes=8, prefix="o")`: key `"|".join([media_id.strip(), str(start_ms), str(end_ms), observer.strip().lower(), label.strip().lower()])`, `prefix + blake2b(key, digest_size=n_bytes).hexdigest()` (17 chars by default). Do not hash score, validation status or project name.
- `add_observation_ids(df, prefix, n_bytes)`: uses `mediaID, eventStart, eventEnd, classifiedBy, scientificName`; only fills rows lacking an ID; raises on missing/null columns and on duplicate IDs (also new vs existing), listing the problematic rows.

## Step 3 - Wire into species_detection
- `nodes.py` (~line 154): drop `observationID = observations.index`; call `add_observation_ids` after renaming columns and before reordering to `observations_pamdp_columns`.
- `utils.py:78`: `classifiedBy = f"birdnet-{analyzer.version}"`.
- `conf/base/parameters/species_detection.yml`: add `observation_id: {prefix: "o", n_bytes: 8}`; pass it to the node in `species_detection/pipeline.py`. Keep the node thin.
- `filter_observations`: unchanged (keeps IDs); add a test.
- `create_manual_annotation_formats`: unchanged now (read-only column / text format deferred to the validation phase).
- grep docs/tests for "Birdnet 2.4" and `observationID == index` and update.

## Step 4 - CLAUDE.md
Create it with: English-only rule, pipeline/catalog/parameters conventions, test command.

## Step 5 - Tests (`src/tests/pipelines/species_detection/`)
- Golden values (must reproduce exactly):
  - ("SON_D001_20240315_063000", 12.5, 15.0, "birdnet-2.4", "Turdus fuscater") -> "o19e702142219ebeb"
  - (..., "birdnet-2.4", "Zonotrichia capensis") -> "o1745ec90d96281ab"
  - (..., "juan.ulloa", "Cyanocorax yncas") -> "o9073a3e025d80234"
  - (..., 12.50, 15.0, " BirdNET-2.4 ", " turdus fuscater") -> "o19e702142219ebeb"
  (already verified in the planning session.)
- Determinism; sensitivity to each field; ms rounding incl. float32 case; prefix and length 17; no ID in a large synthetic sample parses as a number.
- Nulls, missing columns, duplicates (also against existing IDs; message lists rows).
- Only rows without ID get one; `filter_observations` preserves IDs.

## Step 6 - Verification
- `/Users/jsulloa/miniconda3/envs/pamflow_env/bin/python -m pytest src/tests -q`
- Re-run `species_detection` on the test data: unique IDs, identical IDs across two runs, show sample rows; regenerate segments/xlsx.
- No commits unless requested.

## Later phases (not now)
- Validation integration: join on `observationID`; manual rows get IDs via the same function (observer = person, label = added species); audit = ID in `unfiltered_observations` or ID equals recomputation for `classificationMethod == "human"`. Make `observationID` read-only/text in the validation sheet.
- Thresholds: unaffected by the ID design.

## Risks
- ID contract change (old outputs invalid; accepted).
- `classifiedBy` visible value changes.
- Files > ~4.6 h if someone recomputed from float32 CSV; mitigated by compute-once rule.
