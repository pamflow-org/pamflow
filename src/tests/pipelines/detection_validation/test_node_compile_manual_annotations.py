import pandas as pd
import pytest

from pamflow.pipelines.detection_validation.nodes import compile_manual_annotations

PARAMS = dict(
    positive_values=["1", "x", "yes"],
    negative_values=["0", "n", "no"],
    uncertain_values=["?"],
    reassigned_values=["reassigned", "r"],
    multitaxa_values=["multitaxa", "m"],
    uncertain_handling="exclude",
    taxa_separator="|",
)


def _sheet(rows):
    return pd.DataFrame(
        rows,
        columns=[
            "observationID",
            "classifiedBy",
            "classificationProbability",
            "scientificNameModel",
            "category",
            "scientificNameValidated",
            "favorite",
        ],
    )


def _run(rows, **overrides):
    sheets = {"sp_a": lambda: _sheet(rows)}
    return compile_manual_annotations(sheets, **{**PARAMS, **overrides})


ROWS = [
    (1, "Birdnet 2.4", 0.9, "Sp a", "x", "", "x"),
    (2, "Birdnet 2.4", 0.8, "Sp a", "no", "", ""),
    (3, "Birdnet 2.4", 0.7, "Sp a", "?", "", ""),
    (4, "Birdnet 2.4", 0.6, "Sp a", "r", "Sp b", ""),
    (5, "Birdnet 2.4", 0.5, "Sp a", "m", "Sp a | Sp c", ""),
    (6, "Birdnet 2.4", 0.4, "Sp a", None, None, None),
]


def test_columns_and_labels():
    validated, summary = _run(ROWS)
    assert list(validated.columns) == [
        "observationID",
        "classifiedBy",
        "scientificNameModel",
        "classificationProbability",
        "classificationTimestamp",
        "category",
        "scientificNameValidated",
        "favorite",
    ]
    assert validated["category"].tolist() == [
        "Positive",
        "Negative",
        "Uncertain",
        "Reassigned",
        "Multitaxa",
    ]
    assert validated["scientificNameValidated"].tolist() == [
        "Sp a",
        "",
        "",
        "Sp b",
        "Sp a|Sp c",
    ]
    assert validated["favorite"].tolist() == [True, False, False, False, False]
    row = summary.iloc[0]
    assert row["n_pending"] == 1
    assert row["n_annotated"] == 5
    assert row["n_reassigned"] == 1
    assert row["n_multitaxa"] == 1


@pytest.mark.parametrize("handling,expected", [("positive", "Positive"), ("negative", "Negative")])
def test_uncertain_handling_recodes(handling, expected):
    validated, summary = _run(ROWS, uncertain_handling=handling)
    assert validated.loc[validated["observationID"] == 3, "category"].item() == expected
    assert summary.iloc[0]["n_uncertain"] == 1


def test_unrecognized_label_raises():
    with pytest.raises(ValueError, match="unrecognized"):
        _run([(1, "b", 0.9, "Sp a", "zzz", "", "")])


def test_multitaxa_with_comma_raises():
    with pytest.raises(ValueError, match="comma"):
        _run([(1, "b", 0.9, "Sp a", "m", "Sp a, Sp c", "")])


def test_multitaxa_needs_two_species():
    with pytest.raises(ValueError, match="at least two"):
        _run([(1, "b", 0.9, "Sp a", "m", "Sp c", "")])


@pytest.mark.parametrize("validated", ["", "Sp a", "Sp b|Sp c"])
def test_reassigned_needs_one_different_species(validated):
    with pytest.raises(ValueError, match="exactly one"):
        _run([(1, "b", 0.9, "Sp a", "r", validated, "")])


def test_overlapping_values_raise():
    with pytest.raises(ValueError, match="overlap"):
        _run(ROWS, multitaxa_values=["x"])


def test_legacy_columns_are_renamed():
    legacy = pd.DataFrame(
        {
            "observationID": [1],
            "classifiedBy": ["Birdnet"],
            "classificationProbability": [0.9],
            "scientificName": ["Sp a"],
            "positive": ["x"],
            "detectedSpecies": [""],
        }
    )
    validated, _ = compile_manual_annotations({"sp_a": legacy}, **PARAMS)
    assert validated["category"].tolist() == ["Positive"]
    assert validated["scientificNameModel"].tolist() == ["Sp a"]


def test_name_on_negative_or_uncertain_row_is_promoted():
    validated, summary = _run(
        [
            (1, "b", 0.9, "Sp a", "no", "Sp b", ""),
            (2, "b", 0.8, "Sp a", "?", "Sp b|Sp c", ""),
            (3, "b", 0.7, "Sp a", "no", "", ""),
        ]
    )
    assert validated["category"].tolist() == ["Reassigned", "Multitaxa", "Negative"]
    assert validated["scientificNameValidated"].tolist() == ["Sp b", "Sp b|Sp c", ""]
    row = summary.iloc[0]
    assert (row["n_reassigned"], row["n_multitaxa"], row["n_negative"]) == (1, 1, 1)


def test_positive_with_extra_species_becomes_multitaxa():
    validated, _ = _run(
        [
            (1, "b", 0.9, "Sp a", "x", "Sp b", ""),
            (2, "b", 0.8, "Sp a", "x", "Sp a|Sp c", ""),
            (3, "b", 0.7, "Sp a", "x", "Sp a", ""),
        ]
    )
    assert validated["category"].tolist() == ["Multitaxa", "Multitaxa", "Positive"]
    assert validated["scientificNameValidated"].tolist() == [
        "Sp a|Sp b",
        "Sp a|Sp c",
        "Sp a",
    ]
