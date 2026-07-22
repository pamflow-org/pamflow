import logging
import pandas as pd
import pytest
from pamflow.pipelines.species_detection.nodes import create_segments


@pytest.fixture
def media():
    """Media metadata for a single source file, 300s long."""
    return pd.DataFrame({
        "mediaID": ["media_001.WAV"],
        "filePath": ["/audio/media_001.WAV"],
        "fileLength": [300.0],
    })


def _observations(scientific_name, n, media_id="media_001.WAV"):
    return pd.DataFrame({
        "mediaID": [media_id] * n,
        "scientificName": [scientific_name] * n,
        "eventStart": [10.0 + i for i in range(n)],
        "eventEnd": [12.0 + i for i in range(n)],
        "classificationProbability": [0.9] * n,
    })


def test_create_segments_caps_at_available_observations_when_below_segment_size(media):
    """Species with fewer observations than segment_size should return all of them, no error."""
    observations = _observations("Canis lupus", n=3)

    result = create_segments(observations, media, segment_size=10, segment_length=2.0)

    assert len(result) == 3


def test_create_segments_samples_exactly_segment_size_when_enough_observations(media):
    """Species with enough observations should still return exactly segment_size rows."""
    observations = _observations("Canis lupus", n=10)

    result = create_segments(observations, media, segment_size=5, segment_length=2.0)

    assert len(result) == 5


def test_create_segments_logs_info_when_capping_occurs(media, caplog):
    """An info-level notice is logged only for species that get capped."""
    observations = pd.concat(
        [_observations("Canis lupus", n=3), _observations("Ursus arctos", n=10)],
        ignore_index=True,
    )

    with caplog.at_level(logging.INFO, logger="pamflow.pipelines.species_detection.nodes"):
        create_segments(observations, media, segment_size=5, segment_length=2.0)

    messages = [record.message for record in caplog.records]
    assert any("Canis lupus" in m and "3 observation" in m for m in messages)
    assert not any("Ursus arctos" in m for m in messages)


def test_create_segments_no_sampling_error_for_mixed_group_sizes(media):
    """Mixed group sizes in one call don't raise and produce correct per-species counts."""
    observations = pd.concat(
        [_observations("Canis lupus", n=3), _observations("Ursus arctos", n=8)],
        ignore_index=True,
    )

    result = create_segments(observations, media, segment_size=5, segment_length=2.0)

    counts = result["scientificName"].value_counts()
    assert counts["Canis lupus"] == 3
    assert counts["Ursus arctos"] == 5


def test_create_segments_columns_computed_for_capped_rows(media):
    """segmentStart/segmentEnd/segmentsFilePath are still computed correctly for capped species."""
    observations = _observations("Canis lupus", n=3)
    segment_length = 2.0

    result = create_segments(observations, media, segment_size=10, segment_length=segment_length)

    assert {"segmentStart", "segmentEnd", "segmentsFilePath"}.issubset(result.columns)
    assert (result["segmentEnd"] - result["segmentStart"]).round(6).eq(segment_length).all()
    assert result["segmentsFilePath"].str.endswith(".WAV").all()
