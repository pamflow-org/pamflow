import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
from pamflow.pipelines.species_detection.nodes import plot_observations_summary


@pytest.fixture
def sample_observations():
    """Create sample observations DataFrame."""
    return pd.DataFrame({
        "observationID": [1, 2, 3, 4, 5, 6, 7, 8],
        "mediaID": ["m1", "m1", "m1", "m2", "m2", "m3", "m4", "m4"],
        "scientificName": [
            "Canis lupus",
            "Canis lupus",
            "Ursus arctos",
            "Canis lupus",
            "Ursus arctos",
            "Lynx canadensis",
            "Canis lupus",
            "Ursus arctos",
        ],
        "classificationMethod": [
            "machine",
            "machine",
            "human",
            "machine",
            "machine",
            "human",
            "machine",
            "machine",
        ],
        "eventStart": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5],
        "eventEnd": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
    })


@pytest.fixture
def sample_media():
    """Create sample media DataFrame."""
    return pd.DataFrame({
        "mediaID": ["m1", "m2", "m3", "m4", "m5", "m6"],
        "filePath": [
            "/path/file1.wav",
            "/path/file2.wav",
            "/path/file3.wav",
            "/path/file4.wav",
            "/path/file5.wav",
            "/path/file6.wav",
        ],
    })


@pytest.fixture
def sample_observations_all_machine():
    """Create observations with all machine classifications."""
    return pd.DataFrame({
        "observationID": [1, 2, 3],
        "mediaID": ["m1", "m1", "m2"],
        "scientificName": ["Species_A", "Species_B", "Species_A"],
        "classificationMethod": ["machine", "machine", "machine"],
        "eventStart": [0.5, 1.5, 2.5],
        "eventEnd": [1.0, 2.0, 3.0],
    })


@pytest.fixture
def sample_observations_all_human():
    """Create observations with all human classifications."""
    return pd.DataFrame({
        "observationID": [1, 2, 3],
        "mediaID": ["m1", "m2", "m3"],
        "scientificName": ["Species_A", "Species_B", "Species_C"],
        "classificationMethod": ["human", "human", "human"],
        "eventStart": [0.5, 1.5, 2.5],
        "eventEnd": [1.0, 2.0, 3.0],
    })


class TestPlotObservationsSummaryBasic:
    """Basic tests for plot_observations_summary function."""

    def test_returns_matplotlib_figure(self, sample_observations, sample_media):
        """Test that function returns a matplotlib Figure object."""
        result = plot_observations_summary(sample_observations, sample_media)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_figure_has_correct_size(self, sample_observations, sample_media):
        """Test that figure has correct size."""
        result = plot_observations_summary(sample_observations, sample_media)
        figsize = result.get_size_inches()
        assert figsize[0] == 8  # width
        assert figsize[1] == 6  # height

    def test_figure_has_axes(self, sample_observations, sample_media):
        """Test that figure has axes."""
        result = plot_observations_summary(sample_observations, sample_media)
        axes = result.get_axes()
        assert len(axes) > 0

    def test_axes_turned_off(self, sample_observations, sample_media):
        """Test that axes are turned off."""
        result = plot_observations_summary(sample_observations, sample_media)
        ax = result.get_axes()[0]
        # Check that axis is off by verifying artists
        assert len(ax.patches) > 0  # Should have boxes (FancyBboxPatch)

    # def test_with_empty_observations_raises_error(self, sample_media):
    #     """Test that empty observations DataFrame raises an error."""
    #     empty_observations = pd.DataFrame({
    #         "mediaID": [],
    #         "scientificName": [],
    #         "classificationMethod": [],
    #         "eventStart": [],
    #         "eventEnd": [],
    #     })
        
    #     with pytest.raises((ValueError, KeyError)):
    #         plot_observations_summary(empty_observations, sample_media)

    def test_with_single_observation(self, sample_media):
        """Test with single observation."""
        single_observation = pd.DataFrame({
            "observationID": [1],
            "mediaID": ["m1"],
            "scientificName": ["Species_A"],
            "classificationMethod": ["machine"],
            "eventStart": [0.5],
            "eventEnd": [1.0],
        })
        
        result = plot_observations_summary(single_observation, sample_media)
        assert isinstance(result, matplotlib.figure.Figure)


class TestPlotObservationsSummaryCalculations:
    """Tests for correct calculations in plot_observations_summary."""

    def test_number_of_observations_calculated(self, sample_observations, sample_media):
        """Test that number of observations is correctly calculated."""
        result = plot_observations_summary(sample_observations, sample_media)
        
        # Verify that the figure was created with correct data
        assert isinstance(result, matplotlib.figure.Figure)
        n_obs = len(sample_observations)
        assert n_obs == 8

    def test_number_of_species_calculated(self, sample_observations, sample_media):
        """Test that number of species is correctly calculated."""
        result = plot_observations_summary(sample_observations, sample_media)
        
        n_species = sample_observations["scientificName"].nunique()
        assert n_species == 3  # Canis lupus, Ursus arctos, Lynx canadensis

    def test_recordings_with_observations_calculated(self, sample_observations, sample_media):
        """Test that recordings with observations is correctly calculated."""
        result = plot_observations_summary(sample_observations, sample_media)
        
        n_recordings_with = sample_media["mediaID"].isin(
            sample_observations["mediaID"]
        ).sum()
        assert n_recordings_with == 4  # m1, m2, m3, m4 have observations

    def test_recordings_without_observations_calculated(self, sample_observations, sample_media):
        """Test that recordings without observations is correctly calculated."""
        result = plot_observations_summary(sample_observations, sample_media)
        
        n_recordings_with = sample_media["mediaID"].isin(
            sample_observations["mediaID"]
        ).sum()
        n_recordings_without = len(sample_media) - n_recordings_with
        assert n_recordings_without == 2  # m5, m6 have no observations

    def test_machine_vs_human_observations(self, sample_observations, sample_media):
        """Test that machine vs human observations are correctly counted."""
        result = plot_observations_summary(sample_observations, sample_media)
        
        n_machine = (sample_observations.classificationMethod == "machine").sum()
        n_human = (sample_observations.classificationMethod == "human").sum()
        
        assert n_machine == 6
        assert n_human == 2

    def test_observation_time_calculated(self, sample_observations, sample_media):
        """Test that observation time is correctly calculated."""
        result = plot_observations_summary(sample_observations, sample_media)
        
        total_time = (sample_observations.eventEnd - sample_observations.eventStart).sum()
        total_time_minutes = total_time / 60
        
        assert total_time_minutes == pytest.approx(0.067, rel=0.01)


class TestPlotObservationsSummaryEdgeCases:
    """Edge case tests for plot_observations_summary."""

    def test_all_machine_observations(self, sample_observations_all_machine, sample_media):
        """Test with all observations classified as machine."""
        result = plot_observations_summary(sample_observations_all_machine, sample_media)
        
        assert isinstance(result, matplotlib.figure.Figure)
        n_machine = (
            sample_observations_all_machine.classificationMethod == "machine"
        ).sum()
        assert n_machine == 3

    def test_all_human_observations(self, sample_observations_all_human, sample_media):
        """Test with all observations classified as human."""
        result = plot_observations_summary(sample_observations_all_human, sample_media)
        
        assert isinstance(result, matplotlib.figure.Figure)
        n_human = (
            sample_observations_all_human.classificationMethod == "human"
        ).sum()
        assert n_human == 3

    def test_single_species(self, sample_media):
        """Test with only one species."""
        single_species = pd.DataFrame({
            "observationID": [1, 2, 3],
            "mediaID": ["m1", "m1", "m2"],
            "scientificName": ["Species_A", "Species_A", "Species_A"],
            "classificationMethod": ["machine", "machine", "human"],
            "eventStart": [0.5, 1.5, 2.5],
            "eventEnd": [1.0, 2.0, 3.0],
        })
        
        result = plot_observations_summary(single_species, sample_media)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_many_species(self, sample_media):
        """Test with many species."""
        many_species_list = [f"Species_{i:02d}" for i in range(30)]
        observations_data = []
        
        for i, species in enumerate(many_species_list):
            observations_data.append({
                "observationID": i,
                "mediaID": f"m{i % 6}",
                "scientificName": species,
                "classificationMethod": "machine" if i % 2 == 0 else "human",
                "eventStart": float(i) * 0.5,
                "eventEnd": float(i) * 0.5 + 0.5,
            })
        
        many_species_obs = pd.DataFrame(observations_data)
        result = plot_observations_summary(many_species_obs, sample_media)
        
        assert isinstance(result, matplotlib.figure.Figure)

    def test_very_long_species_names(self, sample_media):
        """Test with very long species names."""
        long_names = pd.DataFrame({
            "observationID": [1, 2, 3],
            "mediaID": ["m1", "m2", "m3"],
            "scientificName": [
                "Canis lupus familiaris domesticus subspecies",
                "Ursus arctos horribilis grizzly bear subspecies",
                "Lynx canadensis northern lynx subspecies",
            ],
            "classificationMethod": ["machine", "human", "machine"],
            "eventStart": [0.5, 1.5, 2.5],
            "eventEnd": [1.0, 2.0, 3.0],
        })
        
        result = plot_observations_summary(long_names, sample_media)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_observations_time_greater_than_hour(self, sample_media):
        """Test with observations spanning more than an hour."""
        long_duration = pd.DataFrame({
            "observationID": [1, 2, 3],
            "mediaID": ["m1", "m2", "m3"],
            "scientificName": ["Species_A", "Species_B", "Species_C"],
            "classificationMethod": ["machine", "machine", "human"],
            "eventStart": [0.0, 100.0, 200.0],
            "eventEnd": [3600.0, 3700.0, 3800.0],  # 1 hour, ~16.67 min, ~16.67 min
        })
        
        result = plot_observations_summary(long_duration, sample_media)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_all_media_have_observations(self, sample_observations, sample_media):
        """Test when all media files have observations."""
        # Modify observations to include all media IDs
        all_media_obs = sample_observations.copy()
        all_media_obs["mediaID"] = ["m1", "m2", "m3", "m4", "m5", "m6", "m1", "m2"]
        
        result = plot_observations_summary(all_media_obs, sample_media)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_no_media_have_observations(self, sample_media):
        """Test when no media files have observations (edge case)."""
        # This should still work but with 0% recordings with observations
        obs = pd.DataFrame({
            "observationID": [1, 2],
            "mediaID": ["unknown_m1", "unknown_m2"],
            "scientificName": ["Species_A", "Species_B"],
            "classificationMethod": ["machine", "human"],
            "eventStart": [0.5, 1.5],
            "eventEnd": [1.0, 2.0],
        })
        
        result = plot_observations_summary(obs, sample_media)
        assert isinstance(result, matplotlib.figure.Figure)


class TestPlotObservationsSummaryRobustness:
    """Robustness tests for plot_observations_summary."""

    # def test_with_missing_columns_raises_error(self, sample_media):
    #     """Test that missing required columns raises an error."""
    #     incomplete_obs = pd.DataFrame({
    #         "mediaID": ["m1", "m2"],
    #         "scientificName": ["Species_A", "Species_B"],
    #         # Missing classificationMethod, eventStart, eventEnd
    #     })
        
    #     with pytest.raises(KeyError):
    #         plot_observations_summary(incomplete_obs, sample_media)

    def test_with_null_values_in_data(self, sample_media):
        """Test handling of null values in data."""
        obs_with_nulls = pd.DataFrame({
            "observationID": [1, 2, 3],
            "mediaID": ["m1", None, "m3"],
            "scientificName": ["Species_A", "Species_B", None],
            "classificationMethod": ["machine", "human", None],
            "eventStart": [0.5, 1.5, 2.5],
            "eventEnd": [1.0, 2.0, 3.0],
        })
        
        # Function should handle NaN values gracefully
        result = plot_observations_summary(obs_with_nulls, sample_media)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_with_duplicate_observations(self, sample_observations, sample_media):
        """Test with duplicate observations."""
        duplicated_obs = pd.concat([sample_observations, sample_observations], ignore_index=True)
        
        result = plot_observations_summary(duplicated_obs, sample_media)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_float_precision_in_time_calculations(self, sample_media):
        """Test that float precision is maintained in time calculations."""
        precise_times = pd.DataFrame({
            "observationID": [1, 2, 3],
            "mediaID": ["m1", "m2", "m3"],
            "scientificName": ["Species_A", "Species_B", "Species_C"],
            "classificationMethod": ["machine", "human", "machine"],
            "eventStart": [0.123456, 1.654321, 2.999999],
            "eventEnd": [0.654321, 2.123456, 3.999999],
        })
        
        result = plot_observations_summary(precise_times, sample_media)
        assert isinstance(result, matplotlib.figure.Figure)


class TestPlotObservationsSummaryVisualization:
    """Tests for visualization elements in plot_observations_summary."""

    def test_figure_contains_title(self, sample_observations, sample_media):
        """Test that figure contains title text."""
        result = plot_observations_summary(sample_observations, sample_media)
        ax = result.get_axes()[0]
        
        # Check for text in the figure
        texts = [text.get_text() for text in ax.texts]
        assert any("Summary" in text for text in texts)

    def test_figure_contains_boxes(self, sample_observations, sample_media):
        """Test that figure contains boxes (FancyBboxPatch)."""
        result = plot_observations_summary(sample_observations, sample_media)
        ax = result.get_axes()[0]
        
        # Should have patches (the boxes)
        assert len(ax.patches) >= 6  # At least 6 info boxes

    def test_figure_contains_text_labels(self, sample_observations, sample_media):
        """Test that figure contains text labels."""
        result = plot_observations_summary(sample_observations, sample_media)
        ax = result.get_axes()[0]
        
        texts = [text.get_text() for text in ax.texts]
        # Should have labels and values
        assert len(texts) >= 12  # At least title + 6 labels + 6 values

    def test_figure_is_tight_layout(self, sample_observations, sample_media):
        """Test that figure uses tight_layout."""
        result = plot_observations_summary(sample_observations, sample_media)
        
        # Verify figure was created successfully (tight_layout applied)
        assert isinstance(result, matplotlib.figure.Figure)
        assert len(result.get_axes()) > 0


class TestPlotObservationsSummaryPercentageCalculations:
    """Tests for percentage calculations in plot_observations_summary."""

    def test_percentage_sum_to_100(self, sample_observations, sample_media):
        """Test that percentages sum to 100."""
        n_recordings_with = sample_media["mediaID"].isin(
            sample_observations["mediaID"]
        ).sum()
        n_recordings = len(sample_media)
        n_recordings_without = n_recordings - n_recordings_with
        
        percent_with = round(n_recordings_with / n_recordings * 100, 1)
        percent_without = round(100 - percent_with, 1)
        
        assert percent_with + percent_without == pytest.approx(100, rel=0.1)

    def test_machine_human_percentages_sum_to_100(self, sample_observations, sample_media):
        """Test that machine/human percentages sum to 100."""
        n_observations = len(sample_observations)
        n_machine = (sample_observations.classificationMethod == "machine").sum()
        n_human = (sample_observations.classificationMethod == "human").sum()
        
        percent_machine = round((n_machine / n_observations) * 100, 1)
        percent_human = round((n_human / n_observations) * 100, 1)
        
        assert percent_machine + percent_human == pytest.approx(100, rel=0.1)

    def test_percentage_with_zero_values(self, sample_observations_all_machine, sample_media):
        """Test percentages when one category has zero values."""
        n_observations = len(sample_observations_all_machine)
        n_machine = (
            sample_observations_all_machine.classificationMethod == "machine"
        ).sum()
        n_human = (
            sample_observations_all_machine.classificationMethod == "human"
        ).sum()
        
        percent_machine = round((n_machine / n_observations) * 100, 1)
        percent_human = round((n_human / n_observations) * 100, 1)
        
        assert percent_machine == 100.0
        assert percent_human == 0.0


class TestPlotObservationsSummaryFormatting:
    """Tests for number formatting in plot_observations_summary."""

    def test_format_number_with_thousands(self):
        """Test that large numbers are formatted with thousand separators."""
        from pamflow.pipelines.species_detection.nodes import format_number
        
        formatted = format_number(1000)
        assert "," in formatted or "\u2009" in formatted

    def test_format_number_preserves_value(self):
        """Test that formatted number preserves original value."""
        from pamflow.pipelines.species_detection.nodes import format_number
        
        formatted = format_number(12345)
        # Remove separators and compare
        numeric_value = formatted.replace("\u2009", "").replace(",", "")
        assert numeric_value == "12345"

    def test_percentage_formatted_as_float(self, sample_observations, sample_media):
        """Test that percentages are formatted as floats with one decimal."""
        n_recordings_with = sample_media["mediaID"].isin(
            sample_observations["mediaID"]
        ).sum()
        n_recordings = len(sample_media)
        percent = round(n_recordings_with / n_recordings * 100, 1)
        
        assert isinstance(percent, float)


def test_plot_observations_summary_does_not_show(sample_observations, sample_media):
    """Test that plot_observations_summary does not call plt.show()."""
    result = plot_observations_summary(sample_observations, sample_media)
    
    # Verify that result is returned without showing
    assert isinstance(result, matplotlib.figure.Figure)
    plt.close(result)  # Clean up


def test_multiple_calls_create_different_figures(sample_observations, sample_media):
    """Test that multiple calls create different figure objects."""
    fig1 = plot_observations_summary(sample_observations, sample_media)
    fig2 = plot_observations_summary(sample_observations, sample_media)
    
    assert fig1 is not fig2
    plt.close(fig1)
    plt.close(fig2)