from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import pytest

from pamflow.pipelines.species_detection import nodes

CALLS = []


def fake_single_file(
    wav_file_path,
    lat,
    lon,
    mediaID,
    deploymentID,
    classifier_model_path=None,
    classifier_labels_path=None,
    min_conf=0.1,
):
    CALLS.append({"lat": lat, "lon": lon, "min_conf": min_conf})
    return [
        {
            "common_name": "Common",
            "scientific_name": "Species a",
            "start_time": 0.0,
            "end_time": 3.0,
            "confidence": 0.5,
            "label": "Species a_Common",
            "mediaID": mediaID,
            "deploymentID": deploymentID,
            "classifiedBy": "Birdnet test",
        }
    ]


@pytest.fixture(autouse=True)
def patch_detection(monkeypatch):
    CALLS.clear()
    monkeypatch.setattr(nodes, "species_detection_single_file", fake_single_file)
    # Do not load the BirdNET model in the worker initializer
    monkeypatch.setattr(nodes, "init_worker", lambda *args: None)
    # Threads share the monkeypatched function, processes would not
    monkeypatch.setattr(
        nodes.concurrent.futures, "ProcessPoolExecutor", ThreadPoolExecutor
    )


def make_inputs():
    media = pd.DataFrame(
        {
            "filePath": ["a.wav", "b.wav"],
            "mediaID": ["m1", "m2"],
            "deploymentID": ["D1", "D1"],
        }
    )
    deployments = pd.DataFrame(
        {"deploymentID": ["D1"], "latitude": [4.6], "longitude": [-74.1]}
    )
    return media, deployments


def test_location_filter_enabled_passes_coordinates():
    media, deployments = make_inputs()
    params = {"n_jobs": 1, "use_location_filter": True, "min_conf": 0.3}
    nodes.species_detection_parallel(media, deployments, params, "America/Bogota")
    assert len(CALLS) == 2
    assert all(c["lat"] == 4.6 and c["lon"] == -74.1 for c in CALLS)
    assert all(c["min_conf"] == 0.3 for c in CALLS)


def test_location_filter_disabled_passes_none():
    media, deployments = make_inputs()
    params = {"n_jobs": 1, "use_location_filter": False, "min_conf": 0.1}
    observations = nodes.species_detection_parallel(
        media, deployments, params, "America/Bogota"
    )
    assert len(CALLS) == 2
    assert all(c["lat"] is None and c["lon"] is None for c in CALLS)
    assert observations.shape[0] == 2


def test_defaults_keep_previous_behavior():
    media, deployments = make_inputs()
    nodes.species_detection_parallel(
        media, deployments, {"n_jobs": 1}, "America/Bogota"
    )
    assert all(c["lat"] == 4.6 and c["min_conf"] == 0.1 for c in CALLS)


@pytest.mark.parametrize("param", ["classifier_model_path", "classifier_labels_path"])
def test_missing_custom_model_file_raises_before_processing(param, tmp_path):
    media, deployments = make_inputs()
    params = {"n_jobs": 1, param: str(tmp_path / "missing_file")}
    with pytest.raises(FileNotFoundError, match=param):
        nodes.species_detection_parallel(media, deployments, params, "America/Bogota")
    assert CALLS == []


def test_worker_initializer_receives_model_paths(monkeypatch, tmp_path):
    model = tmp_path / "model.tflite"
    labels = tmp_path / "labels.txt"
    model.write_bytes(b"")
    labels.write_text("Genus species_Common name\n")
    received = []
    monkeypatch.setattr(nodes, "init_worker", lambda *args: received.append(args))
    media, deployments = make_inputs()
    params = {
        "n_jobs": 1,
        "classifier_model_path": str(model),
        "classifier_labels_path": str(labels),
    }
    nodes.species_detection_parallel(media, deployments, params, "America/Bogota")
    assert received and received[0] == (str(model), str(labels))
