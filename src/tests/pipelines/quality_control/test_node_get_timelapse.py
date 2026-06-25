""" 
Unit tests for the get_timelapse node in the quality control pipeline.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from pamflow.pipelines.quality_control.nodes import get_timelapse


@pytest.fixture
def sample_sensor_deployment_data():
    """Create sample sensor deployment data."""
    return pd.DataFrame({
        "deploymentID": ["sensor1", "sensor1", "sensor2", "sensor2", "sensor1"],
        "timestamp": pd.to_datetime([
            "2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02", "2024-01-03"
        ]).date,
        "count": [5, 3, 2, 4, 6]
    })


@pytest.fixture
def sample_media():
    """Create sample media DataFrame."""
    return pd.DataFrame({
        "deploymentID": ["sensor1", "sensor1", "sensor2", "sensor2"],
        "timestamp": pd.to_datetime([
            "2024-01-01 10:00:00",
            "2024-01-01 12:00:00",
            "2024-01-01 11:00:00",
            "2024-01-01 13:00:00"
        ]),
        "filePath": [
            "/path/to/file1.wav",
            "/path/to/file2.wav",
            "/path/to/file3.wav",
            "/path/to/file4.wav"
        ]
    })


@pytest.fixture
def plot_params():
    """Create sample plot parameters."""
    return {
        "nperseg": 512,
        "noverlap": 256,
        "db_range": 80,
        "fig_width": 12,
        "fig_height": 6,
        "colormap": "viridis",
        "flims": [0, 22050]
    }


@patch('pamflow.pipelines.quality_control.nodes.sound.spectrogram')
@patch('pamflow.pipelines.quality_control.nodes.util.plot_spectrogram')
@patch('pamflow.pipelines.quality_control.nodes.concat_audio')
def test_get_timelapse_with_explicit_date(
    mock_concat, mock_plot_spec, mock_spectrogram,
    sample_sensor_deployment_data, sample_media, plot_params
):
    """Test timelapse generation with explicit sample_date."""
    # Setup mocks
    mock_wav = np.random.rand(44100)
    mock_fs = 44100
    mock_concat.return_value = (mock_wav, mock_fs)
    
    mock_spectrogram.return_value = (
        np.random.rand(257, 100),  # Sxx
        np.arange(100),             # tn
        np.arange(257),             # fn
        [0, 1, 100, 22050]          # ext
    )
    
    results = list(get_timelapse(
        sample_sensor_deployment_data,
        sample_media,
        sample_len=10,
        sample_period="5T",
        sample_date="2024-01-01",
        plot_params=plot_params
    ))
    
    assert len(results) > 0
    for audio_dict, fig_dict in results:
        assert isinstance(audio_dict, dict)
        assert isinstance(fig_dict, dict)
        assert len(audio_dict) == len(fig_dict)
        for key in audio_dict.keys():
            assert key in fig_dict
            wav, fs = audio_dict[key]
            assert isinstance(wav, np.ndarray)
            assert fs == mock_fs


# @patch('pamflow.pipelines.quality_control.nodes.sound.spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.util.plot_spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.concat_audio')
# def test_get_timelapse_auto_date_selection(
#     mock_concat, mock_plot_spec, mock_spectrogram,
#     sample_sensor_deployment_data, sample_media, plot_params
# ):
#     """Test automatic date selection (highest sensors + recordings)."""
#     mock_wav = np.random.rand(44100)
#     mock_fs = 44100
#     mock_concat.return_value = (mock_wav, mock_fs)
    
#     mock_spectrogram.return_value = (
#         np.random.rand(257, 100),
#         np.arange(100),
#         np.arange(257),
#         [0, 1, 100, 22050]
#     )
    
#     results = list(get_timelapse(
#         sample_sensor_deployment_data,
#         sample_media,
#         sample_len=10,
#         sample_period="5T",
#         sample_date=None,
#         plot_params=plot_params
#     ))
    
#     assert len(results) > 0


# @patch('pamflow.pipelines.quality_control.nodes.sound.spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.util.plot_spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.concat_audio')
# def test_get_timelapse_yields_correct_structure(
#     mock_concat, mock_plot_spec, mock_spectrogram,
#     sample_sensor_deployment_data, sample_media, plot_params
# ):
#     """Test that generator yields correct key structure."""
#     mock_wav = np.random.rand(44100)
#     mock_fs = 44100
#     mock_concat.return_value = (mock_wav, mock_fs)
    
#     mock_spectrogram.return_value = (
#         np.random.rand(257, 100),
#         np.arange(100),
#         np.arange(257),
#         [0, 1, 100, 22050]
#     )
    
#     for audio_dict, fig_dict in get_timelapse(
#         sample_sensor_deployment_data,
#         sample_media,
#         sample_len=10,
#         sample_period="5T",
#         sample_date="2024-01-01",
#         plot_params=plot_params
#     ):
#         # Keys should follow pattern: "{deploymentID}_timelapse_{date}"
#         for key in audio_dict.keys():
#             assert "timelapse" in key
#             assert "2024-01-01" in key
#             assert key in fig_dict


# @patch('pamflow.pipelines.quality_control.nodes.sound.spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.util.plot_spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.concat_audio')
# def test_get_timelapse_concat_audio_called(
#     mock_concat, mock_plot_spec, mock_spectrogram,
#     sample_sensor_deployment_data, sample_media, plot_params
# ):
#     """Test that concat_audio is called with correct parameters."""
#     mock_wav = np.random.rand(44100)
#     mock_fs = 44100
#     mock_concat.return_value = (mock_wav, mock_fs)
    
#     mock_spectrogram.return_value = (
#         np.random.rand(257, 100),
#         np.arange(100),
#         np.arange(257),
#         [0, 1, 100, 22050]
#     )
    
#     list(get_timelapse(
#         sample_sensor_deployment_data,
#         sample_media,
#         sample_len=15,
#         sample_period="10T",
#         sample_date="2024-01-01",
#         plot_params=plot_params
#     ))
    
#     assert mock_concat.called
#     call_args = mock_concat.call_args
#     assert call_args[1]["sample_len"] == 15


# @patch('pamflow.pipelines.quality_control.nodes.sound.spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.util.plot_spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.concat_audio')
# def test_get_timelapse_spectrogram_called(
#     mock_concat, mock_plot_spec, mock_spectrogram,
#     sample_sensor_deployment_data, sample_media, plot_params
# ):
#     """Test that spectrogram is called with correct plot parameters."""
#     mock_wav = np.random.rand(44100)
#     mock_fs = 44100
#     mock_concat.return_value = (mock_wav, mock_fs)
    
#     mock_spectrogram.return_value = (
#         np.random.rand(257, 100),
#         np.arange(100),
#         np.arange(257),
#         [0, 1, 100, 22050]
#     )
    
#     list(get_timelapse(
#         sample_sensor_deployment_data,
#         sample_media,
#         sample_len=10,
#         sample_period="5T",
#         sample_date="2024-01-01",
#         plot_params=plot_params
#     ))
    
#     assert mock_spectrogram.called
#     call_kwargs = mock_spectrogram.call_args[1]
#     assert call_kwargs["nperseg"] == 512
#     assert call_kwargs["noverlap"] == 256
#     assert call_kwargs["flims"] == [0, 22050]


# @patch('pamflow.pipelines.quality_control.nodes.sound.spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.util.plot_spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.concat_audio')
# def test_get_timelapse_empty_data(
#     mock_concat, mock_plot_spec, mock_spectrogram,
#     plot_params
# ):
#     """Test behavior with empty media data for selected date."""
#     empty_sensor_data = pd.DataFrame({
#         "deploymentID": ["sensor1"],
#         "timestamp": pd.to_datetime(["2024-01-01"]).date,
#         "count": [5]
#     })
    
#     empty_media = pd.DataFrame({
#         "deploymentID": [],
#         "timestamp": pd.to_datetime([]),
#         "filePath": []
#     })
    
#     results = list(get_timelapse(
#         empty_sensor_data,
#         empty_media,
#         sample_len=10,
#         sample_period="5T",
#         sample_date="2024-01-01",
#         plot_params=plot_params
#     ))
    
#     assert len(results) == 0


# @patch('pamflow.pipelines.quality_control.nodes.sound.spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.util.plot_spectrogram')
# @patch('pamflow.pipelines.quality_control.nodes.concat_audio')
# @patch('pamflow.pipelines.quality_control.nodes.plt.close')
# def test_get_timelapse_closes_figures(
#     mock_close, mock_concat, mock_plot_spec, mock_spectrogram,
#     sample_sensor_deployment_data, sample_media, plot_params
# ):
#     """Test that matplotlib figures are closed after yielding."""
#     mock_wav = np.random.rand(44100)
#     mock_fs = 44100
#     mock_concat.return_value = (mock_wav, mock_fs)
    
#     mock_spectrogram.return_value = (
#         np.random.rand(257, 100),
#         np.arange(100),
#         np.arange(257),
#         [0, 1, 100, 22050]
#     )
    
#     list(get_timelapse(
#         sample_sensor_deployment_data,
#         sample_media,
#         sample_len=10,
#         sample_period="5T",
#         sample_date="2024-01-01",
#         plot_params=plot_params
#     ))
    
#     assert mock_close.called