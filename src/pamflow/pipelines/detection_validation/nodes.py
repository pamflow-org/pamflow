import logging

import pandas as pd

logger = logging.getLogger(__name__)


def _normalize_value(value):
    """Casts a raw ``positive`` cell to a comparable string, or None if it is empty.

    Concatenating per-species sheets where some are still fully empty (float NaN
    column) with sheets that already hold booleans upcasts the boolean column to
    float64, turning ``True``/``False`` into ``1.0``/``0.0``. Collapsing
    whole-number floats to plain integer strings keeps that case matching the
    same ``"1"``/``"0"`` entries used for genuine free-text annotations.
    """
    if pd.isna(value):
        return None
    is_whole_number = (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and float(value).is_integer()
    )
    if is_whole_number:
        text = str(int(value))
    else:
        text = str(value)
    text = text.strip().lower()
    return text if text != "" else None


def compile_manual_annotations(
    manual_annotations,
    positive_values,
    negative_values,
    uncertain_values,
    uncertain_handling,
):
    """Compiles the per-species manual annotation spreadsheets into a single table.

    This node concatenates every sheet produced by `species_detection`'s
    `create_manual_annotation_formats` node, normalizes the free-text `positive`
    column into three categories (`positive` / `negative` / `uncertain`), and
    applies `uncertain_handling`. The input corresponds to the catalog entry
    `manual_annotations@PartitionedDataset`. The outputs are stored in the
    catalog as `validated_annotations@pandas` and
    `manual_annotation_summary@pandas`.

    Parameters
    ----------
    manual_annotations : dict
        A dictionary where the keys are partition names (one per species) and the
        values are functions that return DataFrames with manual annotations for
        each species. Loaded from the catalog entry
        `manual_annotations@PartitionedDataset`.

    positive_values : list of str
        Raw `positive` cell values (case/whitespace-insensitive) that count as a
        confirmed detection. Passed as
        `params:detection_validation_parameters.positive_values`.

    negative_values : list of str
        Raw `positive` cell values that count as a confirmed non-detection. Passed as
        `params:detection_validation_parameters.negative_values`.

    uncertain_values : list of str
        Raw `positive` cell values that count as an inconclusive annotation. Passed as
        `params:detection_validation_parameters.uncertain_values`.

    uncertain_handling : str
        How to treat rows classified as `uncertain`: `exclude` (default) keeps them
        labelled as `uncertain` in the output — they are counted and reported, but
        `fit_precision_models` (Step 2) is expected to leave them out of the fit.
        `positive` / `negative` recodes them to that category instead, so the
        pipeline can be run twice to obtain lower/upper bounds on the threshold.
        Passed as `params:detection_validation_parameters.uncertain_handling`.

    Returns
    -------
    pandas.DataFrame
        One row per annotated segment (rows left blank in the `.xlsx` files are
        dropped, after being logged as pending). Carries `observationID`,
        `scientificName`, `detectedSpecies`, `classifiedBy`,
        `classificationTimestamp`, `classificationProbability`, `eventStart`,
        `eventEnd`, `segmentsFilePath`, `filePath`, `sourceFile` (the originating
        `.xlsx` partition name), and `positive` normalized to
        `positive` / `negative` / `uncertain`. Stored in the catalog as
        `validated_annotations@pandas`.

    pandas.DataFrame
        One row per species with `scientificName`, `n_pending`, `n_annotated`,
        `n_positive`, `n_negative`, `n_uncertain`. Counts reflect the raw
        annotation categories *before* `uncertain_handling` recodes anything, so
        `n_uncertain` always shows the true number of inconclusive annotations
        regardless of how the fit will treat them. Stored in the catalog as
        `manual_annotation_summary@pandas`.
    """
    positive_set = {_normalize_value(v) for v in positive_values}
    negative_set = {_normalize_value(v) for v in negative_values}
    uncertain_set = {_normalize_value(v) for v in uncertain_values}

    overlap = (positive_set & negative_set) | (positive_set & uncertain_set) | (
        negative_set & uncertain_set
    )
    if overlap:
        raise ValueError(
            "positive_values/negative_values/uncertain_values overlap on: "
            f"{sorted(overlap)}. Each raw value must map to exactly one "
            "category — fix conf/base/parameters/detection_validation.yml."
        )

    frames = []
    for partition_name, load_func in manual_annotations.items():
        df = load_func() if callable(load_func) else load_func
        df = df.copy()
        df["sourceFile"] = partition_name
        frames.append(df)

    annotations = pd.concat(frames, ignore_index=True)

    normalized = annotations["positive"].apply(_normalize_value)
    pending_mask = normalized.isna()

    pending_counts = (
        annotations.loc[pending_mask]
        .groupby("scientificName")
        .size()
        .rename("n_pending")
        .sort_index()
    )
    for species, n_pending in pending_counts.items():
        logger.info(
            f"{species}: {n_pending} segment(s) pending annotation "
            "(empty 'positive' cell)."
        )

    def _classify(text):
        if text in positive_set:
            return "positive"
        if text in negative_set:
            return "negative"
        if text in uncertain_set:
            return "uncertain"
        return "unrecognized"

    category = normalized.where(pending_mask, normalized.apply(_classify))
    unrecognized_mask = (~pending_mask) & (category == "unrecognized")

    if unrecognized_mask.any():
        bad_rows = annotations.loc[unrecognized_mask]
        bad_normalized = normalized.loc[unrecognized_mask]
        details = "\n".join(
            f"  - value={row['positive']!r} (normalized={bad_normalized.loc[idx]!r}) "
            f"file={row['sourceFile']} scientificName={row.get('scientificName')} "
            f"observationID={row.get('observationID')}"
            for idx, row in bad_rows.iterrows()
        )
        raise ValueError(
            f"Found {unrecognized_mask.sum()} unrecognized value(s) in the "
            f"'positive' column:\n{details}\n"
            "Add them to positive_values/negative_values/uncertain_values in "
            "conf/base/parameters/detection_validation.yml, or fix the "
            "source .xlsx file."
        )

    summary = pd.DataFrame(
        {
            "scientificName": annotations["scientificName"],
            "category": category,
            "is_pending": pending_mask,
        }
    )
    summary = summary.groupby("scientificName").agg(
        n_pending=("is_pending", "sum"),
        n_positive=("category", lambda s: (s == "positive").sum()),
        n_negative=("category", lambda s: (s == "negative").sum()),
        n_uncertain=("category", lambda s: (s == "uncertain").sum()),
    )
    summary["n_annotated"] = (
        summary["n_positive"] + summary["n_negative"] + summary["n_uncertain"]
    )
    summary = summary[
        ["n_pending", "n_annotated", "n_positive", "n_negative", "n_uncertain"]
    ].reset_index().sort_values("scientificName").reset_index(drop=True)

    annotations = annotations.loc[~pending_mask].copy()
    annotations["positive"] = category.loc[~pending_mask]

    if uncertain_handling == "exclude":
        pass
    elif uncertain_handling in ("positive", "negative"):
        annotations.loc[
            annotations["positive"] == "uncertain", "positive"
        ] = uncertain_handling
    else:
        raise ValueError(
            f"Unknown uncertain_handling: {uncertain_handling!r}. "
            "Expected 'exclude', 'positive', or 'negative'."
        )

    columns = [
        "observationID",
        "scientificName",
        "detectedSpecies",
        "classifiedBy",
        "classificationTimestamp",
        "classificationProbability",
        "eventStart",
        "eventEnd",
        "segmentsFilePath",
        "filePath",
        "sourceFile",
        "positive",
    ]
    annotations = annotations[columns].reset_index(drop=True)

    logger.info(
        f"Compiled {len(annotations)} annotated segment(s) across "
        f"{annotations['scientificName'].nunique()} species "
        f"({int((annotations['positive'] == 'positive').sum())} positive, "
        f"{int((annotations['positive'] == 'negative').sum())} negative, "
        f"{int((annotations['positive'] == 'uncertain').sum())} uncertain)."
    )

    return annotations, summary
