import numpy as np
import pandas as pd

from pamflow.pipelines.detection_validation.nodes import fit_precision_models

PARAMS = dict(
    min_annotations=15,
    min_per_class=3,
    confidence_level=0.95,
    score_transform="identity",
)


def test_fit_uses_only_positive_and_negative_labels():
    rng = np.random.default_rng(0)
    score = np.linspace(0.1, 0.99, 40)
    positive = rng.random(40) < score
    category = np.where(positive, "Positive", "Negative").astype(object)
    category[:3] = ["Reassigned", "Multitaxa", "Uncertain"]
    validated = pd.DataFrame(
        {
            "scientificNameModel": "Sp a",
            "classificationProbability": score,
            "category": category,
        }
    )
    summary = pd.DataFrame(
        {
            "scientificNameModel": ["Sp a", "Sp z"],
            "n_pending": [0, 5],
            "n_annotated": [40, 0],
            "n_positive": [0, 0],
            "n_negative": [0, 0],
            "n_uncertain": [0, 0],
        }
    )
    fits, _ = fit_precision_models(validated, PARAMS, summary)
    assert set(fits["scientificName"]) == {"Sp a", "Sp z"}
    row = fits.set_index("scientificName").loc["Sp a"]
    assert row["n_uncertain"] == 1
    assert row["n_positive"] + row["n_negative"] == 37
    assert fits.set_index("scientificName").loc["Sp z", "status"] == "insufficient_sample"
