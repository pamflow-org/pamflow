"""
Unit tests for the plot_survey_effort function in the quality control pipeline.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from pamflow.pipelines.quality_control.nodes import plot_survey_effort


@pytest.fixture
def sample_media_summary():
    """Create sample media summary DataFrame."""
    return pd.DataFrame({
        "deploymentID": ["sensor1", "sensor2", "sensor3", "sensor4"],
        "date_ini": pd.to_datetime([
            "2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"
        ]),
        "date_end": pd.to_datetime([
            "2024-01-10", "2024-01-15", "2024-01-20", "2024-01-25"
        ]),
        "n_recordings": [10, 15, 20, 25]
    })


@pytest.fixture
def sample_deployments():
    """Create sample deployments DataFrame."""
    return pd.DataFrame({
        "deploymentID": ["sensor1", "sensor2", "sensor3", "sensor4"],
        "locationID": ["loc1", "loc2", "loc3", "loc4"],
        "latitude": [40.7128, 34.0522, 41.8781, 39.7392],
        "longitude": [-74.0060, -118.2437, -87.6298, -104.9903]
    })


@pytest.fixture
def sample_media():
    """Create sample media DataFrame."""
    return pd.DataFrame({
        "deploymentID": ["sensor1", "sensor2", "sensor3", "sensor4"],
        "timestamp": pd.to_datetime([
            "2024-01-01 10:00:00",
            "2024-01-05 12:00:00",
            "2024-01-10 11:00:00",
            "2024-01-15 13:00:00"
        ]),
        "filePath": [
            "/path/to/file1.wav",
            "/path/to/file2.wav",
            "/path/to/file3.wav",
            "/path/to/file4.wav"
        ],
        "fileLength": [3600, 7200, 5400, 10800]  # in seconds
    })


def test_plot_survey_effort_returns_figure(
    sample_media_summary, sample_deployments, sample_media
):
    """Test that plot_survey_effort returns a matplotlib Figure."""
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
        fig = plot_survey_effort(sample_media_summary, sample_deployments, sample_media)
        assert isinstance(fig, Figure)
        plt.close(fig)


def test_plot_survey_effort_basic_functionality(
    sample_media_summary, sample_deployments, sample_media
):
    """Test basic functionality with valid data."""
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame') as mock_gdf:
        mock_gdf_instance = MagicMock()
        mock_polygon = MagicMock()
        mock_polygon.area = 5_000_000  # 5 km²
        mock_gdf_instance.union_all.return_value.convex_hull = mock_polygon
        mock_gdf.return_value = mock_gdf_instance

        fig = plot_survey_effort(sample_media_summary, sample_deployments, sample_media)

        assert isinstance(fig, Figure)
        ax = fig.axes[0]
        
        # Verify that text elements are added (Survey Effort title)
        text_elements = [t.get_text() for t in ax.texts]
        assert "Survey Effort" in text_elements
        plt.close(fig)


def test_plot_survey_effort_calculates_deployments(
    sample_media_summary, sample_deployments, sample_media
):
    """Test that number of deployments is calculated correctly."""
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
        fig = plot_survey_effort(sample_media_summary, sample_deployments, sample_media)
        ax = fig.axes[0]
        
        text_elements = [t.get_text() for t in ax.texts]
        # Should have 4 deployments in the output
        assert any("4" in text for text in text_elements if text)
        plt.close(fig)


def test_plot_survey_effort_calculates_recordings(
    sample_media_summary, sample_deployments, sample_media
):
    """Test that number of recordings is calculated correctly."""
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
        fig = plot_survey_effort(sample_media_summary, sample_deployments, sample_media)
        ax = fig.axes[0]
        
        text_elements = [t.get_text() for t in ax.texts]
        # Should have 4 recordings
        assert any("4" in text for text in text_elements if text)
        plt.close(fig)


def test_plot_survey_effort_calculates_recording_time(
    sample_media_summary, sample_deployments, sample_media
):
    """Test that total recording time is calculated correctly."""
    # Total fileLength = 3600 + 7200 + 5400 + 10800 = 27000 seconds = 7.5 hours
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
        fig = plot_survey_effort(sample_media_summary, sample_deployments, sample_media)
        ax = fig.axes[0]
        
        text_elements = [t.get_text() for t in ax.texts]
        # Should find 7.5 or similar
        assert any("7.5" in text for text in text_elements if text)
        plt.close(fig)


def test_plot_survey_effort_few_locations_returns_na(
    sample_media_summary, sample_deployments, sample_media
):
    """Test that spatial coverage shows 'N/A' when fewer than 4 locations."""
    # Modify deployments to have only 2 locations
    sample_deployments_small = sample_deployments.iloc[:2].copy()
    sample_deployments_small["locationID"] = ["loc1", "loc1"]
    
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
        fig = plot_survey_effort(sample_media_summary, sample_deployments_small, sample_media)
        ax = fig.axes[0]
        
        text_elements = [t.get_text() for t in ax.texts]
        # Should have N/A for spatial coverage
        assert any("N/A" in text for text in text_elements if text)
        plt.close(fig)


def test_plot_survey_effort_calculates_temporal_coverage(
    sample_media_summary, sample_deployments, sample_media
):
    """Test that temporal coverage is calculated correctly."""
    # date_ini min: 2024-01-01, date_end max: 2024-01-25
    # Coverage: 24 days
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
        fig = plot_survey_effort(sample_media_summary, sample_deployments, sample_media)
        ax = fig.axes[0]
        
        text_elements = [t.get_text() for t in ax.texts]
        # Should find 24 days
        assert any("24" in text for text in text_elements if text)
        plt.close(fig)


def test_plot_survey_effort_locations_count(
    sample_media_summary, sample_deployments, sample_media
):
    """Test that number of locations is counted correctly."""
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
        fig = plot_survey_effort(sample_media_summary, sample_deployments, sample_media)
        ax = fig.axes[0]
        
        text_elements = [t.get_text() for t in ax.texts]
        # Should have 4 locations
        assert any("4" in text for text in text_elements if text)
        plt.close(fig)


# @patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame')
# def test_plot_survey_effort_spatial_coverage_calculated(
#     mock_gdf, sample_media_summary, sample_deployments, sample_media
# ):
#     """Test that spatial coverage (convex hull area) is calculated correctly."""
#     mock_gdf_instance = MagicMock()
#     mock_polygon = MagicMock()
#     mock_polygon.area = 10_000_000  # 10 km²
#     mock_gdf_instance.union_all.return_value.convex_hull = mock_polygon
#     mock_gdf_instance.estimate_utm_crs.return_value = "EPSG:32633"
#     mock_gdf.return_value = mock_gdf_instance

#     fig = plot_survey_effort(sample_media_summary, sample_deployments, sample_media)
#     ax = fig.axes[0]
    
#     text_elements = [t.get_text() for t in ax.texts]
#     # Should have 10 km² for spatial coverage
#     assert any("10" in text for text in text_elements if text)
#     plt.close(fig)


# def test_plot_survey_effort_figure_layout(
#     sample_media_summary, sample_deployments, sample_media
# ):
#     """Test that figure has correct layout structure."""
#     with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
#         fig = plot_survey_effort(sample_media_summary, sample_deployments, sample_media)
#         ax = fig.axes[0]
        
#         # Verify axes is off (for infographic style)
#         assert not ax.get_xticks().any() or len(ax.get_xticks()) == 0 or ax.get_xaxis().get_visible() == False
        
#         # Verify figure size is reasonable
#         assert fig.get_figwidth() == 8.0
#         assert fig.get_figheight() == 6.0
#         plt.close(fig)


def test_plot_survey_effort_empty_media(
    sample_media_summary, sample_deployments
):
    """Test behavior with empty media DataFrame."""
    empty_media = pd.DataFrame({
        "deploymentID": [],
        "timestamp": pd.to_datetime([]),
        "filePath": [],
        "fileLength": []
    })
    
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
        fig = plot_survey_effort(sample_media_summary, sample_deployments, empty_media)
        assert isinstance(fig, Figure)
        plt.close(fig)


def test_plot_survey_effort_single_deployment(
    sample_media_summary, sample_deployments, sample_media
):
    """Test with single deployment."""
    single_deployment = sample_deployments.iloc[:1].copy()
    single_summary = sample_media_summary.iloc[:1].copy()
    
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
        fig = plot_survey_effort(single_summary, single_deployment, sample_media)
        assert isinstance(fig, Figure)
        plt.close(fig)


def test_plot_survey_effort_survey_effort_title_present(
    sample_media_summary, sample_deployments, sample_media
):
    """Test that 'Survey Effort' title is present in the figure."""
    with patch('pamflow.pipelines.quality_control.nodes.gpd.GeoDataFrame'):
        fig = plot_survey_effort(sample_media_summary, sample_deployments, sample_media)
        ax = fig.axes[0]
        
        text_elements = [t.get_text() for t in ax.texts]
        assert "Survey Effort" in text_elements
        plt.close(fig)