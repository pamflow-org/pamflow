import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure

from pamflow.pipelines.quality_control.nodes import detect_audio_outliers

PARAMS = {
    "z_threshold": 3.5,
    "max_labeled_deployments": 50,
    "fig_width": 8,
    "fig_height": 5,
}


def make_media(n=20, outliers=True):
    rows = []
    for dep in ["A", "B"]:
        for i in range(n):
            rows.append({
                "deploymentID": dep,
                "mediaID": f"{dep}_{i}",
                "timestamp": pd.Timestamp("2024-01-01") + pd.Timedelta(hours=i),
                "fileLength": 60.0 + (0.1 * (i % 3) if dep == "A" else 0.0),
                "sampleRate": 48000.0,
                "filePath": f"/data/{dep}_{i}.wav",
            })
    df = pd.DataFrame(rows)
    if outliers:
        df.loc[df.mediaID == "A_0", "fileLength"] = 5.0          # length only
        df.loc[df.mediaID == "A_1", "sampleRate"] = 16000.0      # rate only
        df.loc[df.mediaID == "B_2", ["fileLength", "sampleRate"]] = [
            30.0, 44100.0]                                       # MAD == 0 deployment, both
    return df


def test_flags_expected_files():
    fig, listing = detect_audio_outliers(make_media(), PARAMS)
    assert isinstance(fig, Figure)
    plt.close(fig)
    variables = dict(zip(listing["mediaID"], listing["variable"]))
    assert variables["A_0"] == "fileLength"
    assert variables["A_1"] == "sampleRate"
    assert variables["B_2"] == "fileLength+sampleRate"
    assert len(listing) == 3
    assert listing.loc[listing.mediaID == "A_0", "median_sampleRate"].iloc[0] == 48000.0


def test_does_not_mutate_input():
    media = make_media()
    before = media.copy()
    fig, _ = detect_audio_outliers(media, PARAMS)
    plt.close(fig)
    pd.testing.assert_frame_equal(media, before)


def test_no_outliers_returns_empty_listing():
    fig, listing = detect_audio_outliers(make_media(outliers=False), PARAMS)
    plt.close(fig)
    assert listing.empty
    assert "variable" in listing.columns
