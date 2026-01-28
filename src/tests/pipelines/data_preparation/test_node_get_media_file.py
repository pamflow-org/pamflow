import os
from pathlib import Path

import pandas as pd
import pytest

from pamflow.pipelines.data_preparation import nodes


def test_get_media_file_basic(tmp_path, monkeypatch):
    # Prepare fake directory structure with two sensors
    sensor_a = tmp_path / "sensorA"
    sensor_b = tmp_path / "sensorB"
    sensor_a.mkdir()
    sensor_b.mkdir()

    # Create fake wav file paths (no need to create actual files for this test)
    file_a = sensor_a / "rec_A.wav"
    file_b = sensor_b / "rec_B.wav"

    # Prepare field_deployments_sheet matching sensors
    field_deployments = pd.DataFrame({"deploymentID": ["sensorA", "sensorB"]})

    # Prepare fake metadata DataFrame returned by maad.util.get_metadata_dir
    fake_metadata = pd.DataFrame(
        [
            {
                "path_audio": str(file_a),
                "fname": "rec_A",
                "bits": 16,
                "sample_rate": 44100,
                "length": 1.23456,
                "channels": 1,
                "sensor_name": "sensorA",
                "date": "2020-01-01 12:00:00",
                "time": "12:00:00",
                "fsize": 1234,
                "samples": 54321,
            },
            {
                "path_audio": str(file_b),
                "fname": "rec_B",
                "bits": 24,
                "sample_rate": 48000,
                "length": 2.34567,
                "channels": 2,
                "sensor_name": "sensorB",
                "date": "2020-01-02 13:30:00",
                "time": "13:30:00",
                "fsize": 2345,
                "samples": 65432,
            },
        ]
    )

    # Monkeypatch the util.get_metadata_dir used inside the node
    monkeypatch.setattr(nodes.util, "get_metadata_dir", lambda path, _: fake_metadata.copy())

    # Call the node
    media = nodes.get_media_file(str(tmp_path), field_deployments, timezone="UTC")

    # Basic assertions about structure and content
    assert "filePath" in media.columns
    assert "mediaID" in media.columns
    assert "deploymentID" in media.columns
    assert "fileName" in media.columns
    assert "fileMediatype" in media.columns
    assert "filePublic" in media.columns
    assert "captureMethod" in media.columns

    # Ensure time-related columns were dropped
    for dropped in ("time", "fsize", "samples"):
        assert dropped not in media.columns

    # fileName is the basename of filePath
    assert media.loc[media["deploymentID"] == "sensorA", "fileName"].iloc[0] == "rec_A.wav"
    assert media.loc[media["deploymentID"] == "sensorB", "fileName"].iloc[0] == "rec_B.wav"

    # fileMediatype and captureMethod constants
    assert (media["fileMediatype"] == "audio/WAV").all()
    assert (media["captureMethod"] == "activityDetection").all()
    assert (media["filePublic"] == False).all()

    # fileLength rounded float
    assert pytest.approx(1.235, rel=1e-3) == float(media.loc[media["deploymentID"] == "sensorA", "fileLength"].iloc[0])
    assert pytest.approx(2.346, rel=1e-3) == float(media.loc[media["deploymentID"] == "sensorB", "fileLength"].iloc[0])

    # timestamp localized to UTC and formatted with +0000 offset
    assert media["timestamp"].str.endswith("+0000").all()