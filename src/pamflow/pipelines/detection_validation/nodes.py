import logging
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib.patches import FancyBboxPatch
from statsmodels.tools.sm_exceptions import PerfectSeparationWarning

logger = logging.getLogger(__name__)

# Clip scores away from 0/1 before taking logit(score), to avoid -inf/+inf.
_LOGIT_EPS = 1e-6

# Fallback guard for near-perfect separation that the exact min/max check below
# does not catch (e.g. a tie at the boundary): a slope standard error this large
# on a [0, 1]-ish predictor scale only happens when the optimizer is chasing an
# unidentified parameter.
_SEPARATION_SE_THRESHOLD = 1e3


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


def _transform_score(score, score_transform):
    """Maps raw classificationProbability scores onto the regression's predictor
    scale."""
    score = score.astype(float)
    if score_transform == "identity":
        return score
    if score_transform == "logit":
        clipped = score.clip(_LOGIT_EPS, 1 - _LOGIT_EPS)
        return np.log(clipped / (1 - clipped))
    raise ValueError(
        f"Unknown score_transform: {score_transform!r}. Expected 'identity' or 'logit'."
    )


def _inverse_transform_score(value, score_transform):
    """Maps a predictor-scale value back onto the original [0, 1] score scale."""
    if score_transform == "identity":
        return value
    if score_transform == "logit":
        return 1.0 / (1.0 + np.exp(-value))
    raise ValueError(
        f"Unknown score_transform: {score_transform!r}. Expected 'identity' or 'logit'."
    )


_EMPTY_FIT_FIELDS = {
    "b0": np.nan,
    "b1": np.nan,
    "b1_se": np.nan,
    "b1_ci_low": np.nan,
    "b1_ci_high": np.nan,
    "loglik_null": np.nan,
    "loglik_full": np.nan,
    "lr_stat": np.nan,
    "p_value": np.nan,
    "pseudo_r2": np.nan,
    "aic": np.nan,
}


def _fit_one_species(species, group, params, alpha):
    """Fits (or short-circuits) the logistic model for a single species.

    Returns a `(fit_record, curve_frame)` tuple; `curve_frame` is `None` unless the
    fit succeeded. Factored out of `fit_precision_models` purely to keep that
    function's statement/argument counts within the lint limit — see its
    docstring for the actual modelling logic and status semantics.
    """
    min_annotations = params["min_annotations"]
    min_per_class = params["min_per_class"]
    score_transform = params["score_transform"]

    fit_group = group[group["positive"].isin(["positive", "negative"])]
    n_positive = int((fit_group["positive"] == "positive").sum())
    n_negative = int((fit_group["positive"] == "negative").sum())
    n_uncertain = int((group["positive"] == "uncertain").sum())
    n_annotated = n_positive + n_negative

    base_record = {
        "scientificName": species,
        "n_annotated": n_annotated,
        "n_positive": n_positive,
        "n_negative": n_negative,
        "n_uncertain": n_uncertain,
        "min_score": float(group["classificationProbability"].min()),
        "max_score": float(group["classificationProbability"].max()),
    }

    sample_ok = (
        n_annotated >= min_annotations
        and n_positive >= min_per_class
        and n_negative >= min_per_class
    )
    if not sample_ok:
        logger.info(
            f"{species}: insufficient_sample (n_annotated={n_annotated}, "
            f"n_positive={n_positive}, n_negative={n_negative}; requires "
            f"min_annotations={min_annotations}, min_per_class={min_per_class})."
        )
        record = {**base_record, "status": "insufficient_sample", **_EMPTY_FIT_FIELDS}
        return record, None

    score = fit_group["classificationProbability"].astype(float)
    y = (fit_group["positive"] == "positive").astype(int)

    perfectly_separated = (
        score[y == 1].min() > score[y == 0].max()
        or score[y == 0].min() > score[y == 1].max()
    )
    if perfectly_separated:
        logger.info(
            f"{species}: separation (every positive/negative score falls on its "
            "own side of a single split point; threshold is not estimable)."
        )
        record = {**base_record, "status": "separation", **_EMPTY_FIT_FIELDS}
        return record, None

    x = _transform_score(score, score_transform)
    X = sm.add_constant(x)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", PerfectSeparationWarning)
        res = sm.Logit(y, X).fit(disp=0)
        separation_warned = any(
            issubclass(w.category, PerfectSeparationWarning) for w in caught
        )

    converged = bool(res.mle_retvals.get("converged", True))
    b1_se = float(res.bse.iloc[1])
    near_separation = (
        separation_warned
        or not converged
        or not np.isfinite(b1_se)
        or b1_se > _SEPARATION_SE_THRESHOLD
    )
    if near_separation:
        logger.info(
            f"{species}: separation (logistic fit did not converge cleanly; "
            f"converged={converged}, b1_se={b1_se})."
        )
        record = {**base_record, "status": "separation", **_EMPTY_FIT_FIELDS}
        return record, None

    ci = res.conf_int(alpha=alpha)
    record = {
        **base_record,
        "status": "fitted",
        "b0": float(res.params.iloc[0]),
        "b1": float(res.params.iloc[1]),
        "b1_se": b1_se,
        "b1_ci_low": float(ci.iloc[1, 0]),
        "b1_ci_high": float(ci.iloc[1, 1]),
        "loglik_null": float(res.llnull),
        "loglik_full": float(res.llf),
        "lr_stat": float(res.llr),
        "p_value": float(res.llr_pvalue),
        "pseudo_r2": float(res.prsquared),
        "aic": float(res.aic),
    }

    grid = np.linspace(base_record["min_score"], base_record["max_score"], 100)
    grid_X = sm.add_constant(
        _transform_score(pd.Series(grid), score_transform), has_constant="add"
    )
    prediction = res.get_prediction(grid_X).summary_frame(alpha=alpha)
    curve_frame = pd.DataFrame(
        {
            "scientificName": species,
            "score": grid,
            "predicted_probability": prediction["predicted"].to_numpy(),
            "ci_low": prediction["ci_lower"].to_numpy(),
            "ci_high": prediction["ci_upper"].to_numpy(),
        }
    )
    return record, curve_frame


def _unannotated_species_record(row):
    """Builds an insufficient_sample record for a species with zero annotated rows.

    Such species never form a group in `validated_annotations` (every one of their
    rows was pending, and `compile_manual_annotations` drops pending rows), so they
    would otherwise be silently missing from `precision_model_fits` instead of
    showing up as `insufficient_sample`. There is no score data to report for them,
    hence `min_score`/`max_score` are `NaN`.
    """
    return {
        "scientificName": row["scientificName"],
        "n_annotated": int(row["n_annotated"]),
        "n_positive": int(row["n_positive"]),
        "n_negative": int(row["n_negative"]),
        "n_uncertain": int(row["n_uncertain"]),
        "min_score": np.nan,
        "max_score": np.nan,
        "status": "insufficient_sample",
        **_EMPTY_FIT_FIELDS,
    }


def fit_precision_models(validated_annotations, params, manual_annotation_summary):
    """Fits a per-species logistic curve of `positive ~ score`.

    For each species in `validated_annotations`, fits
    `sm.Logit(y, sm.add_constant(f(score)))` where `y` is 1 for `positive` rows and
    0 for `negative` rows (`uncertain` rows are always left out of the fit itself,
    regardless of `uncertain_handling`, since they are not a resolved 0/1 outcome).
    The inputs correspond to the catalog entries `validated_annotations@pandas` and
    `manual_annotation_summary@pandas`. The outputs are stored in the catalog as
    `precision_model_fits@pandas` and `precision_curves@pandas`.

    Before fitting, two checks can short-circuit a species straight to a diagnostic
    `status`, with every fit-related column left as `NaN`:

    - `n_annotated < min_annotations`, or fewer than `min_per_class`
      positives/negatives → `status = "insufficient_sample"`. This also covers
      species with *zero* annotated rows: they never form a group in
      `validated_annotations` (every row was pending and got dropped in Step 1),
      so `manual_annotation_summary` — which lists every species regardless of
      how much of it is annotated — is what lets this node report them as
      `insufficient_sample` instead of silently omitting them.
    - Perfect separation (every positive score above every negative score, or vice
      versa) → `status = "separation"`. Checked directly on the sorted scores
      first; a fit that nonetheless fails to converge or returns a huge slope
      standard error is caught as the same status, as a safety net for
      near-separation.

    Species that pass both checks get `status = "fitted"`; the final
    species-level verdict (`ok` / `score_not_informative` / `negative_slope` /
    `target_unreachable` / `target_always_met`) is decided downstream by
    `recommend_thresholds`, since it also needs `target_precision`.

    Parameters
    ----------
    validated_annotations : pandas.DataFrame
        Compiled manual annotations. Loaded from the catalog entry
        `validated_annotations@pandas`. Must carry `scientificName`,
        `classificationProbability`, and `positive`
        (`positive` / `negative` / `uncertain`).

    params : dict
        The full `detection_validation_parameters` dict. Passed as
        `params:detection_validation_parameters`. Uses `min_annotations`,
        `min_per_class`, `confidence_level`, and `score_transform`.

    manual_annotation_summary : pandas.DataFrame
        Per-species annotation counts from Step 1, including species with zero
        annotated rows. Loaded from the catalog entry
        `manual_annotation_summary@pandas`. Must carry `scientificName`,
        `n_annotated`, `n_positive`, `n_negative`, `n_uncertain`.

    Returns
    -------
    pandas.DataFrame
        One row per species listed in `manual_annotation_summary` (not just those
        with at least one annotation): `scientificName`, `n_annotated`,
        `n_positive`, `n_negative`, `n_uncertain`, `min_score`, `max_score`,
        `status`, `b0`, `b1`, `b1_se`, `b1_ci_low`, `b1_ci_high`, `loglik_null`,
        `loglik_full`, `lr_stat`, `p_value` (the likelihood-ratio test p-value),
        `pseudo_r2` (McFadden), `aic`. Stored in the catalog as
        `precision_model_fits@pandas`.

    pandas.DataFrame
        Long-format table for plotting: `scientificName`, `score`,
        `predicted_probability`, `ci_low`, `ci_high`, over a 100-point grid
        spanning each fitted species' observed score range. Only includes
        species with `status = "fitted"`. Stored in the catalog as
        `precision_curves@pandas`.
    """
    alpha = 1 - params["confidence_level"]

    fit_records = []
    curve_frames = []
    species_with_annotations = set()

    for species, group in validated_annotations.groupby("scientificName"):
        species_with_annotations.add(species)
        record, curve_frame = _fit_one_species(species, group, params, alpha)
        fit_records.append(record)
        if curve_frame is not None:
            curve_frames.append(curve_frame)

    unannotated = manual_annotation_summary[
        ~manual_annotation_summary["scientificName"].isin(species_with_annotations)
    ]
    for _, row in unannotated.iterrows():
        logger.info(
            f"{row['scientificName']}: insufficient_sample (n_annotated=0, "
            f"{int(row['n_pending'])} segment(s) still pending)."
        )
        fit_records.append(_unannotated_species_record(row))

    fits = (
        pd.DataFrame(fit_records).sort_values("scientificName").reset_index(drop=True)
    )
    curve_columns = [
        "scientificName",
        "score",
        "predicted_probability",
        "ci_low",
        "ci_high",
    ]
    if curve_frames:
        curves = pd.concat(curve_frames, ignore_index=True)
    else:
        curves = pd.DataFrame(columns=curve_columns)

    n_fitted = (fits["status"] == "fitted").sum()
    logger.info(f"Fitted a logistic model for {n_fitted}/{len(fits)} species.")

    return fits, curves


def recommend_thresholds(
    precision_model_fits, target_precision, significance_level, score_transform
):
    """Inverts each species' fitted curve to recommend a working score threshold.

    Solves `f(t*) = (logit(target_precision) - b0) / b1` in closed form (`f` being
    `identity` or `logit` per `score_transform`) and classifies each species into one
    final `status`. The input corresponds to the catalog entry
    `precision_model_fits@pandas`. The output is stored in the catalog as
    `detection_validation_summary@pandas`.

    Note on parameters: the plan's node signature lists only `(precision_model_fits,
    target_precision)`, but resolving `score_not_informative` vs. `ok` needs
    `significance_level`, and inverting the curve back to the original score scale
    needs `score_transform` — both are passed explicitly here rather than assumed.

    Parameters
    ----------
    precision_model_fits : pandas.DataFrame
        Per-species model fits. Loaded from the catalog entry
        `precision_model_fits@pandas`.

    target_precision : float
        Minimum desired probability of a correct detection at the threshold. Passed as
        `params:detection_validation_parameters.target_precision`.

    significance_level : float
        LR test threshold below which the score is considered informative for a
        species. Passed as `params:detection_validation_parameters.significance_level`.

    score_transform : str
        `identity` or `logit` — must match the value used in `fit_precision_models`, to
        invert the fitted curve back onto the original score scale. Passed as
        `params:detection_validation_parameters.score_transform`.

    Returns
    -------
    pandas.DataFrame
        One row per species: `scientificName`, `status`
        (`ok` / `insufficient_sample` / `separation` / `score_not_informative` /
        `negative_slope` / `target_unreachable` / `target_always_met`),
        `n_annotated`, `n_positive`, `n_negative`, `n_uncertain`, `b0`, `b1`,
        `b1_ci_low`, `b1_ci_high`, `p_value`, `min_score`, `max_score`, `t_star`
        (the recommended threshold; `NaN` unless `status` is `ok`,
        `target_unreachable`, or `target_always_met`), and
        `fitted_probability_at_t_star` (should equal `target_precision` whenever
        `t_star` is defined — a built-in check on the closed-form inversion).
        Stored in the catalog as `detection_validation_summary@pandas`.
    """
    logit_target = float(np.log(target_precision / (1 - target_precision)))

    no_threshold = {"t_star": np.nan, "fitted_probability_at_t_star": np.nan}

    def _resolve(row):
        if row["status"] in ("insufficient_sample", "separation"):
            return pd.Series({"status": row["status"], **no_threshold})

        if row["p_value"] >= significance_level:
            return pd.Series({"status": "score_not_informative", **no_threshold})

        if row["b1"] < 0:
            return pd.Series({"status": "negative_slope", **no_threshold})

        f_t_star = (logit_target - row["b0"]) / row["b1"]
        t_star = float(_inverse_transform_score(f_t_star, score_transform))

        if t_star > row["max_score"]:
            status = "target_unreachable"
        elif t_star < row["min_score"]:
            status = "target_always_met"
        else:
            status = "ok"

        return pd.Series(
            {
                "status": status,
                "t_star": t_star,
                "fitted_probability_at_t_star": target_precision,
            }
        )

    resolved = precision_model_fits.apply(_resolve, axis=1)

    summary = precision_model_fits[
        [
            "scientificName",
            "n_annotated",
            "n_positive",
            "n_negative",
            "n_uncertain",
            "b0",
            "b1",
            "b1_ci_low",
            "b1_ci_high",
            "p_value",
            "min_score",
            "max_score",
        ]
    ].copy()
    summary["status"] = resolved["status"]
    summary["t_star"] = resolved["t_star"]
    summary["fitted_probability_at_t_star"] = resolved["fitted_probability_at_t_star"]

    status_counts = summary["status"].value_counts()
    logger.info(f"Threshold recommendation status counts:\n{status_counts.to_string()}")

    return summary


def _format_stat(value, fmt="{:.3g}"):
    """Formats a possibly-NaN diagnostic number for display on a figure."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "n/a"
    return fmt.format(value)


def _plot_one_species(species, annotations, curve, summary_row, pseudo_r2):
    """Builds the single-panel diagnostic figure for one species.

    Factored out of `plot_precision_models` to keep that function short — see its
    docstring for what each plot element means and why.
    """
    fig, ax = plt.subplots(figsize=(7, 5))

    # Passed as .to_numpy() throughout this function: with this environment's
    # numpy/matplotlib/pandas combination, matplotlib's fill_between crashes on
    # raw pandas Series (masked_invalid can't call np.isfinite on them) even
    # though the dtype is plain float64.
    resolved = annotations[annotations["positive"].isin(["positive", "negative"])]
    y = (resolved["positive"] == "positive").astype(float)
    jitter = np.random.default_rng(abs(hash(species)) % (2**32)).uniform(
        -0.04, 0.04, size=len(y)
    )
    ax.scatter(
        resolved["classificationProbability"].to_numpy(),
        (y + jitter).to_numpy(),
        s=35,
        alpha=0.7,
        color="black",
        zorder=3,
        label="annotated segment",
    )

    uncertain = annotations[annotations["positive"] == "uncertain"]
    if not uncertain.empty:
        jitter_u = np.random.default_rng(abs(hash(species)) % (2**32) + 1).uniform(
            -0.04, 0.04, size=len(uncertain)
        )
        ax.scatter(
            uncertain["classificationProbability"].to_numpy(),
            0.5 + jitter_u,
            s=35,
            alpha=0.7,
            color="gray",
            marker="^",
            zorder=3,
            label="uncertain",
        )

    if not curve.empty:
        ax.plot(
            curve["score"].to_numpy(),
            curve["predicted_probability"].to_numpy(),
            color="tab:blue",
            linewidth=2,
            label="fitted P(positive)",
        )
        ax.fill_between(
            curve["score"].to_numpy(),
            curve["ci_low"].to_numpy(),
            curve["ci_high"].to_numpy(),
            color="tab:blue",
            alpha=0.2,
            label="confidence band",
        )

    status = summary_row["status"]
    if status == "ok":
        target_precision = summary_row["fitted_probability_at_t_star"]
        t_star = summary_row["t_star"]
        ax.axhline(
            target_precision,
            color="tab:red",
            linestyle="--",
            linewidth=1,
            label=f"target_precision={target_precision:.2f}",
        )
        ax.axvline(
            t_star,
            color="tab:green",
            linestyle="--",
            linewidth=1,
            label=f"t*={t_star:.3f}",
        )

    n_positive = int(summary_row["n_positive"])
    n_negative = int(summary_row["n_negative"])
    annotation_text = "\n".join(
        [
            f"n = {int(summary_row['n_annotated'])}",
            f"positive/negative = {n_positive}/{n_negative}",
            f"p-value = {_format_stat(summary_row['p_value'])}",
            f"pseudo-R² = {_format_stat(pseudo_r2)}",
        ]
    )
    ax.text(
        0.02,
        0.98,
        annotation_text,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox={
            "boxstyle": "round",
            "facecolor": "white",
            "alpha": 0.85,
            "edgecolor": "lightgray",
        },
    )

    title = species if status == "ok" else f"{species} — {status}"
    ax.set_title(title)
    ax.set_xlabel("classificationProbability (score)")
    ax.set_ylabel("P(positive)")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.15, 1.15)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()

    return fig


def plot_precision_models(
    validated_annotations,
    precision_curves,
    detection_validation_summary,
    precision_model_fits,
):
    """Plots one diagnostic figure per species: annotations, fitted curve, threshold.

    One panel per species: individual annotations as jittered points at
    `y ∈ {0, 1}` (`uncertain` rows, if any survived `uncertain_handling`, are shown
    separately at `y = 0.5`), the fitted logistic curve with its confidence band (for
    species with `status = "ok"` in `precision_model_fits`, i.e. a curve exists),
    and — **only when `status == "ok"`** — a horizontal line at `target_precision`
    and a vertical line at `t*`. Species with any other `status` are still plotted
    (points, and the curve/band if one exists) but without those threshold lines,
    and with the status appended to the title. A text box in the corner always shows
    `n`, `n_positive`/`n_negative`, `p_value`, and `pseudo_r2` — so the underlying
    sample size stays visible even when the curve itself looks convincing.
    The inputs correspond to the catalog entries `validated_annotations@pandas`,
    `precision_curves@pandas`, `detection_validation_summary@pandas`, and
    `precision_model_fits@pandas`. The output is stored in the catalog as
    `detection_validation_plots@PartitionedDataset`.

    Note on parameters: the plan's node signature lists only `(validated_annotations,
    precision_curves, detection_validation_summary)`, but the `pseudo_r2` the figure
    is required to show only lives in `precision_model_fits` — added here as a
    fourth input for the same reason `manual_annotation_summary` was added to
    `fit_precision_models`.

    Parameters
    ----------
    validated_annotations : pandas.DataFrame
        Compiled manual annotations. Loaded from the catalog entry
        `validated_annotations@pandas`.

    precision_curves : pandas.DataFrame
        Per-species fitted curve grid. Loaded from the catalog entry
        `precision_curves@pandas`. Empty (no rows) for a species means no curve
        could be fit for it.

    detection_validation_summary : pandas.DataFrame
        Per-species recommended thresholds and final status. Loaded from the
        catalog entry `detection_validation_summary@pandas`. Iterated to decide
        which species get a figure (every species in this table gets one).

    precision_model_fits : pandas.DataFrame
        Per-species model fits. Loaded from the catalog entry
        `precision_model_fits@pandas`. Only `pseudo_r2` is used here.

    Yields
    ------
    dict
        `{scientificName (spaces replaced with underscores): matplotlib.figure.Figure}`,
        one at a time. Stored in the catalog as
        `detection_validation_plots@PartitionedDataset`.
    """
    pseudo_r2_by_species = precision_model_fits.set_index("scientificName")["pseudo_r2"]

    for _, summary_row in detection_validation_summary.iterrows():
        species = summary_row["scientificName"]
        annotations = validated_annotations[
            validated_annotations["scientificName"] == species
        ]
        curve = precision_curves[precision_curves["scientificName"] == species]
        pseudo_r2 = pseudo_r2_by_species.get(species, np.nan)

        fig = _plot_one_species(species, annotations, curve, summary_row, pseudo_r2)
        yield {"_".join(species.split()): fig}
        plt.close(fig)


def _draw_overview_cards(ax, cards):
    """Draws the top row of value/label cards, matching the style of
    `species_detection.plot_observations_summary`."""
    ax.axis("off")
    n = len(cards)
    card_w, card_h = 0.28, 0.7
    x_margin = 0.04
    x_spacing = (1 - 2 * x_margin - n * card_w) / max(n - 1, 1)
    y = 0.1
    for i, (value, label) in enumerate(cards):
        x = x_margin + i * (card_w + x_spacing)
        box = FancyBboxPatch(
            (x, y),
            card_w,
            card_h,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            linewidth=1,
            edgecolor="lightgray",
            facecolor="white",
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(
            x + card_w / 2,
            y + card_h * 0.62,
            str(value),
            ha="center",
            va="center",
            fontsize=20,
            weight="bold",
            transform=ax.transAxes,
        )
        ax.text(
            x + card_w / 2,
            y + card_h * 0.28,
            label,
            ha="center",
            va="center",
            fontsize=11,
            color="gray",
            transform=ax.transAxes,
        )


_STATUS_ORDER = [
    "ok",
    "target_unreachable",
    "target_always_met",
    "negative_slope",
    "score_not_informative",
    "separation",
    "insufficient_sample",
]


def plot_validation_overview(detection_validation_summary):
    """Plots an aggregate infographic across all species, in the style of
    `species_detection.plot_observations_summary`.

    Top row: card counts for species with a recommended threshold, total annotated
    segments, and total uncertain annotations. Bottom row: a bar chart of species
    counts by `status` (so it's clear at a glance how many species still lack a
    usable threshold and why), and a bar chart of the recommended `t*` for every
    species with `status = "ok"`. The input corresponds to the catalog entry
    `detection_validation_summary@pandas`. The output is stored in the catalog as
    `detection_validation_overview@matplotlib`.

    Parameters
    ----------
    detection_validation_summary : pandas.DataFrame
        Per-species recommended thresholds and final status. Loaded from the
        catalog entry `detection_validation_summary@pandas`.

    Returns
    -------
    matplotlib.figure.Figure
        The aggregate infographic. Stored in the catalog as
        `detection_validation_overview@matplotlib`.
    """
    n_species_total = len(detection_validation_summary)
    n_species_ok = int((detection_validation_summary["status"] == "ok").sum())
    n_total_annotated = int(detection_validation_summary["n_annotated"].sum())
    n_uncertain = int(detection_validation_summary["n_uncertain"].sum())

    status_counts = (
        detection_validation_summary["status"]
        .value_counts()
        .reindex(_STATUS_ORDER)
        .dropna()
        .astype(int)
    )

    ok_thresholds = detection_validation_summary.loc[
        detection_validation_summary["status"] == "ok", ["scientificName", "t_star"]
    ].sort_values("t_star")

    fig = plt.figure(figsize=(11, 8))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.6], hspace=0.45, wspace=0.3)

    cards_ax = fig.add_subplot(gs[0, :])
    cards = [
        (f"{n_species_ok}/{n_species_total}", "Species with\nrecommended threshold"),
        (f"{n_total_annotated:,}", "Total annotated\nsegments"),
        (f"{n_uncertain:,}", "Uncertain\nannotations"),
    ]
    _draw_overview_cards(cards_ax, cards)
    cards_ax.text(
        0,
        1.05,
        "Detection validation overview",
        fontsize=16,
        weight="bold",
        transform=cards_ax.transAxes,
    )

    status_ax = fig.add_subplot(gs[1, 0])
    labels = status_counts.index[::-1].tolist()
    values = status_counts.to_numpy()[::-1]
    status_ax.barh(labels, values, color="tab:blue")
    for y_pos, val in enumerate(values):
        status_ax.text(val, y_pos, f" {val}", va="center", fontsize=9)
    status_ax.set_xlabel("Number of species")
    status_ax.set_title("Species by status")

    threshold_ax = fig.add_subplot(gs[1, 1])
    if ok_thresholds.empty:
        threshold_ax.axis("off")
        threshold_ax.text(
            0.5,
            0.5,
            "No species reached status = ok",
            ha="center",
            va="center",
            color="gray",
        )
    else:
        threshold_ax.barh(
            ok_thresholds["scientificName"].to_numpy(),
            ok_thresholds["t_star"].to_numpy(),
            color="tab:green",
        )
        for y_pos, val in enumerate(ok_thresholds["t_star"]):
            threshold_ax.text(val, y_pos, f" {val:.2f}", va="center", fontsize=9)
        threshold_ax.set_xlim(0, 1)
        threshold_ax.set_xlabel("Recommended threshold (t*)")
    threshold_ax.set_title("Recommended thresholds")

    fig.subplots_adjust(left=0.18, right=0.96, top=0.9, bottom=0.08)

    return fig
