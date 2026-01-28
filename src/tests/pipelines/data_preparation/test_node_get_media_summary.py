import pandas as pd
import pytest

from pamflow.pipelines.data_preparation import nodes


def test_get_media_summary_basic():
    # Build a media DataFrame with two deployments and known intervals
    rows = [
        # sensorA: 3 recordings at 0s, 10s, 20s
        {"deploymentID": "sensorA", "timestamp": "2020-01-01T00:00:00+0000", "fileLength": 1.0, "sampleRate": 44100},
        {"deploymentID": "sensorA", "timestamp": "2020-01-01T00:00:20+0000", "fileLength": 2.0, "sampleRate": 44100},
        {"deploymentID": "sensorA", "timestamp": "2020-01-01T00:00:10+0000", "fileLength": 1.5, "sampleRate": 44100},
        # sensorB: 2 recordings at 0s, 30s
        {"deploymentID": "sensorB", "timestamp": "2020-02-01T12:00:00+0000", "fileLength": 2.0, "sampleRate": 48000},
        {"deploymentID": "sensorB", "timestamp": "2020-02-01T12:00:30+0000", "fileLength": 2.5, "sampleRate": 48000},
    ]
    media = pd.DataFrame(rows)

    summary = nodes.get_media_summary(media)

    # Basic shape and keys
    assert set(["deploymentID", "date_ini", "date_end", "n_recordings", "time_diff", "sample_length", "sample_rate", "duration"]).issubset(
        set(summary.columns)
    )

    # Counts
    assert int(summary.loc[summary["deploymentID"] == "sensorA", "n_recordings"].iloc[0]) == 3
    assert int(summary.loc[summary["deploymentID"] == "sensorB", "n_recordings"].iloc[0]) == 2

    # Median sample_length
    assert pytest.approx(1.5) == float(summary.loc[summary["deploymentID"] == "sensorA", "sample_length"].iloc[0])
    assert pytest.approx(2.25) == float(summary.loc[summary["deploymentID"] == "sensorB", "sample_length"].iloc[0])

    # sample_rate mode
    assert int(summary.loc[summary["deploymentID"] == "sensorA", "sample_rate"].iloc[0]) == 44100
    assert int(summary.loc[summary["deploymentID"] == "sensorB", "sample_rate"].iloc[0]) == 48000

    # time_diff and duration as timedeltas
    assert summary.loc[summary["deploymentID"] == "sensorA", "time_diff"].iloc[0] == pd.Timedelta(seconds=10)
    assert summary.loc[summary["deploymentID"] == "sensorA", "duration"].iloc[0] == pd.Timedelta(seconds=20)
    assert summary.loc[summary["deploymentID"] == "sensorB", "time_diff"].iloc[0] == pd.Timedelta(seconds=30)
    assert summary.loc[summary["deploymentID"] == "sensorB", "duration"].iloc[0] == pd.Timedelta(seconds=30)