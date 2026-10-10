import json

import numpy as np
import pandas as pd
import pytest

from pamflow.pipelines.export.nodes import (
    from_deployments_to_deployments_gbif,
    from_media_to_media_gbif,
    from_observations_to_observations_gbif,
)


def test_media_gbif_packs_audio_columns_as_json():
    media = pd.DataFrame(
        {
            "mediaID": ["a"],
            "sampleRate": [44100],
            "bitDepth": [16],
            "fileLength": [60.0],
            "numChannels": [np.nan],
        }
    )
    out = from_media_to_media_gbif(media)
    assert list(out.columns) == ["mediaID", "exifData"]
    assert json.loads(out.loc[0, "exifData"]) == {
        "sampleRate": 44100,
        "bitDepth": 16,
        "fileLength": 60.0,
        "numChannels": None,
    }
    assert "exifData" not in media.columns  # input not mutated


def test_deployments_gbif_renames_and_merges_tags():
    deployments = pd.DataFrame(
        {
            "recorderID": ["r1", "r2"],
            "recorderModel": ["m", "m"],
            "recorderHeight": [1.0, 2.0],
            "recorderDepth": [np.nan, np.nan],
            "recorderTilt": [0, 0],
            "recorderHeading": [0, 0],
            "recorderConfiguration": ["cfg", np.nan],
            "deploymentTags": ["tag1", np.nan],
        }
    )
    out = from_deployments_to_deployments_gbif(deployments)
    assert "cameraID" in out.columns and "cameraHeading" in out.columns
    assert "recorderConfiguration" not in out.columns
    assert out.loc[0, "deploymentTags"] == "tag1 | cfg"
    assert pd.isna(out.loc[1, "deploymentTags"])  # not the string "nan"


def _obs_media():
    media = pd.DataFrame(
        {
            "mediaID": ["a"],
            "timestamp": pd.to_datetime(["2024-01-01 06:00:00"]).tz_localize("UTC"),
        }
    )
    obs = pd.DataFrame(
        {
            "mediaID": ["a"],
            "eventStart": [1.0],
            "eventEnd": [3.0],
            "frequencyLow": [100.0],
            "frequencyHigh": [200.0],
        }
    )
    return obs, media


def test_observations_gbif_absolute_iso_times():
    obs, media = _obs_media()
    out = from_observations_to_observations_gbif(obs, media)
    assert out.loc[0, "eventStart"] == "2024-01-01T06:00:01+0000"
    assert out.loc[0, "eventEnd"] == "2024-01-01T06:00:03+0000"
    assert out.loc[0, "observationLevel"] == "media"
    assert not {"timestamp", "frequencyLow", "frequencyHigh"} & set(out.columns)


def test_observations_gbif_unknown_media_raises():
    obs, media = _obs_media()
    obs["mediaID"] = "zzz"
    with pytest.raises(ValueError):
        from_observations_to_observations_gbif(obs, media)
