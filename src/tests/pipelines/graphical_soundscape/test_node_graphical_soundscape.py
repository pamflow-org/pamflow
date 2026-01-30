import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, call
import matplotlib.pyplot as plt
from pamflow.pipelines.graphical_soundscape.nodes import graphical_soundscape_pamflow


@pytest.fixture
def sample_media():
    """Create sample media DataFrame with multiple deployments."""
    return pd.DataFrame({
        "mediaID": ["media_001", "media_002", "media_003", "media_004", "media_005"],
        "filePath": [
            "/path/to/deployment1/file1.wav",
            "/path/to/deployment1/file2.wav",
            "/path/to/deployment1/file3.wav",
            "/path/to/deployment2/file4.wav",
            "/path/to/deployment2/file5.wav",
        ],
        "deploymentID": ["D1", "D1", "D1", "D2", "D2"],
        "timestamp": pd.to_datetime([
            "2024-01-01 08:30:00",
            "2024-01-01 12:15:00",
            "2024-01-01 18:45:00",
            "2024-01-02 10:00:00",
            "2024-01-02 14:30:00",
        ]),
        "fileLength": [3600, 3600, 3600, 3600, 3600],
    })


@pytest.fixture
def sample_media_zero_length():
    """Create sample media with some zero-length files."""
    return pd.DataFrame({
        "mediaID": ["media_001", "media_002", "media_003"],
        "filePath": [
            "/path/to/file1.wav",
            "/path/to/file2.wav",
            "/path/to/file3.wav",
        ],
        "deploymentID": ["D1", "D1", "D1"],
        "timestamp": pd.to_datetime([
            "2024-01-01 08:30:00",
            "2024-01-01 12:15:00",
            "2024-01-01 18:45:00",
        ]),
        "fileLength": [3600, 0, 3600],
    })


@pytest.fixture
def sample_graphical_soundscape_parameters():
    """Create sample graphical soundscape parameters."""
    return {
        "threshold_abs": -40,
        "target_fs": 22050,
        "nperseg": 512,
        "noverlap": 256,
        "db_range": 80,
        "min_distance": 10,
        "n_jobs": 2,
    }


@pytest.fixture
def sample_graphical_soundscape_output():
    """Create sample graphical soundscape output DataFrame."""
    return pd.DataFrame({
        "time_min": [0.5, 1.2, 2.3],
        "freq_peak_hz": [2000, 3500, 1500],
        "amp_db": [-20, -25, -18],
        "durationBW_hz": [500, 400, 600],
    })


def test_graphical_soundscape_pamflow_returns_generator(
    sample_media, sample_graphical_soundscape_parameters
):
    """Test that graphical_soundscape_pamflow returns a generator."""
    with patch(
        "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
    ) as mock_gs:
        mock_gs.return_value = pd.DataFrame()
        
        with patch("matplotlib.pyplot.subplots") as mock_subplots:
            mock_fig, mock_ax = MagicMock(), MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            result = graphical_soundscape_pamflow(
                sample_media, sample_graphical_soundscape_parameters
            )
            
            # Check that it's a generator
            assert hasattr(result, "__iter__")
            assert hasattr(result, "__next__")


# def test_graphical_soundscape_pamflow_yields_dict_tuples(
#     sample_media, sample_graphical_soundscape_parameters, sample_graphical_soundscape_output
# ):
#     """Test that function yields tuples of (data_dict, figure_dict)."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = sample_graphical_soundscape_output
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             with patch("matplotlib.pyplot.close") as mock_close:
#                 result = graphical_soundscape_pamflow(
#                     sample_media, sample_graphical_soundscape_parameters
#                 )
                
#                 results_list = list(result)
                
#                 # Should yield 2 results (one per deployment)
#                 assert len(results_list) == 2
                
#                 # Each result should be a tuple of 2 dicts
#                 for data_dict, figure_dict in results_list:
#                     assert isinstance(data_dict, dict)
#                     assert isinstance(figure_dict, dict)


# def test_graphical_soundscape_pamflow_processes_multiple_deployments(
#     sample_media, sample_graphical_soundscape_parameters
# ):
#     """Test that function processes each deployment separately."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = pd.DataFrame()
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             list(graphical_soundscape_pamflow(
#                 sample_media, sample_graphical_soundscape_parameters
#             ))
            
#             # graphical_soundscape_maad should be called once per deployment
#             assert mock_gs.call_count == 2


# def test_graphical_soundscape_pamflow_correct_deployment_data(
#     sample_media, sample_graphical_soundscape_parameters
# ):
#     """Test that each deployment receives correct filtered data."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = pd.DataFrame()
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             list(graphical_soundscape_pamflow(
#                 sample_media, sample_graphical_soundscape_parameters
#             ))
            
#             # Check that correct data was passed to graphical_soundscape_maad
#             calls = mock_gs.call_args_list
            
#             # First call should have 3 files from D1
#             first_call_data = calls[0][0][0]
#             assert len(first_call_data) == 3
#             assert (first_call_data["deploymentID"] == "D1").all()
            
#             # Second call should have 2 files from D2
#             second_call_data = calls[1][0][0]
#             assert len(second_call_data) == 2
#             assert (second_call_data["deploymentID"] == "D2").all()


# def test_graphical_soundscape_pamflow_excludes_zero_length_files(
#     sample_media_zero_length, sample_graphical_soundscape_parameters
# ):
#     """Test that files with zero length are excluded."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = pd.DataFrame()
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             list(graphical_soundscape_pamflow(
#                 sample_media_zero_length, sample_graphical_soundscape_parameters
#             ))
            
#             # Should only process 2 files (zero-length file excluded)
#             call_data = mock_gs.call_args_list[0][0][0]
#             assert len(call_data) == 2
#             assert (call_data["fileLength"] > 0).all()


# def test_graphical_soundscape_pamflow_adds_date_column(
#     sample_media, sample_graphical_soundscape_parameters
# ):
#     """Test that date column is added to media."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = pd.DataFrame()
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             list(graphical_soundscape_pamflow(
#                 sample_media, sample_graphical_soundscape_parameters
#             ))
            
#             # Check that date column was created
#             call_data = mock_gs.call_args_list[0][0][0]
#             assert "date" in call_data.columns


# def test_graphical_soundscape_pamflow_adds_time_column(
#     sample_media, sample_graphical_soundscape_parameters
# ):
#     """Test that time (hour) column is extracted."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = pd.DataFrame()
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             list(graphical_soundscape_pamflow(
#                 sample_media, sample_graphical_soundscape_parameters
#             ))
            
#             # Check that time column was created with hour values
#             call_data = mock_gs.call_args_list[0][0][0]
#             assert "time" in call_data.columns
#             assert all(0 <= hour <= 23 for hour in call_data["time"])


# def test_graphical_soundscape_pamflow_passes_correct_parameters(
#     sample_media, sample_graphical_soundscape_parameters
# ):
#     """Test that correct parameters are passed to graphical_soundscape_maad."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = pd.DataFrame()
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             list(graphical_soundscape_pamflow(
#                 sample_media, sample_graphical_soundscape_parameters
#             ))
            
#             # Get first call arguments
#             args, kwargs = mock_gs.call_args_list[0]
            
#             # Check positional arguments
#             assert args[1] == sample_graphical_soundscape_parameters["threshold_abs"]
#             assert args[2] == "filePath"
#             assert args[3] == "time"
#             assert args[4] == sample_graphical_soundscape_parameters["target_fs"]
#             assert args[5] == sample_graphical_soundscape_parameters["nperseg"]
#             assert args[6] == sample_graphical_soundscape_parameters["noverlap"]
#             assert args[7] == sample_graphical_soundscape_parameters["db_range"]
#             assert args[8] == sample_graphical_soundscape_parameters["min_distance"]
#             assert args[9] == sample_graphical_soundscape_parameters["n_jobs"]


# def test_graphical_soundscape_pamflow_yields_correct_key_names(
#     sample_media, sample_graphical_soundscape_parameters, sample_graphical_soundscape_output
# ):
#     """Test that yielded dictionaries have correct key names."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = sample_graphical_soundscape_output
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             with patch("matplotlib.pyplot.close"):
#                 results = list(graphical_soundscape_pamflow(
#                     sample_media, sample_graphical_soundscape_parameters
#                 ))
                
#                 # Check first deployment result
#                 data_dict_1, figure_dict_1 = results[0]
#                 assert "graph_D1" in data_dict_1
#                 assert "graph_D1" in figure_dict_1
                
#                 # Check second deployment result
#                 data_dict_2, figure_dict_2 = results[1]
#                 assert "graph_D2" in data_dict_2
#                 assert "graph_D2" in figure_dict_2


# def test_graphical_soundscape_pamflow_data_dict_contains_dataframe(
#     sample_media, sample_graphical_soundscape_parameters, sample_graphical_soundscape_output
# ):
#     """Test that data dictionary contains DataFrame."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = sample_graphical_soundscape_output
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             with patch("matplotlib.pyplot.close"):
#                 results = list(graphical_soundscape_pamflow(
#                     sample_media, sample_graphical_soundscape_parameters
#                 ))
                
#                 data_dict, _ = results[0]
#                 assert isinstance(data_dict["graph_D1"], pd.DataFrame)


# def test_graphical_soundscape_pamflow_figure_dict_contains_figure(
#     sample_media, sample_graphical_soundscape_parameters, sample_graphical_soundscape_output
# ):
#     """Test that figure dictionary contains matplotlib Figure."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = sample_graphical_soundscape_output
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             with patch("matplotlib.pyplot.close"):
#                 results = list(graphical_soundscape_pamflow(
#                     sample_media, sample_graphical_soundscape_parameters
#                 ))
                
#                 _, figure_dict = results[0]
#                 assert figure_dict["graph_D1"] == mock_fig


def test_graphical_soundscape_pamflow_plot_graph_called(
    sample_media, sample_graphical_soundscape_parameters, sample_graphical_soundscape_output
):
    """Test that plot_graph is called for each deployment."""
    with patch(
        "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
    ) as mock_gs:
        mock_gs.return_value = sample_graphical_soundscape_output
        
        with patch("matplotlib.pyplot.subplots") as mock_subplots:
            mock_fig, mock_ax = MagicMock(), MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            with patch(
                "pamflow.pipelines.graphical_soundscape.nodes.plot_graph"
            ) as mock_plot_graph:
                with patch("matplotlib.pyplot.close"):
                    list(graphical_soundscape_pamflow(
                        sample_media, sample_graphical_soundscape_parameters
                    ))
                    
                    # plot_graph should be called twice (once per deployment)
                    assert mock_plot_graph.call_count == 2


# def test_graphical_soundscape_pamflow_closes_figures(
#     sample_media, sample_graphical_soundscape_parameters, sample_graphical_soundscape_output
# ):
#     """Test that figures are closed after processing."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = sample_graphical_soundscape_output
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             with patch("matplotlib.pyplot.close") as mock_close:
#                 list(graphical_soundscape_pamflow(
#                     sample_media, sample_graphical_soundscape_parameters
#                 ))
                
#                 # plt.close should be called twice (once per deployment)
#                 assert mock_close.call_count == 2


def test_graphical_soundscape_pamflow_empty_media():
    """Test with empty media DataFrame."""
    empty_media = pd.DataFrame({
        "mediaID": [],
        "filePath": [],
        "deploymentID": [],
        "timestamp": [],
        "fileLength": [],
    })
    
    params = {
        "threshold_abs": -40,
        "target_fs": 22050,
        "nperseg": 512,
        "noverlap": 256,
        "db_range": 80,
        "min_distance": 10,
        "n_jobs": 2,
    }
    
    with patch(
        "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
    ) as mock_gs:
        mock_gs.return_value = pd.DataFrame()
        
        results = list(graphical_soundscape_pamflow(empty_media, params))
        
        # Should return empty generator
        assert len(results) == 0


# def test_graphical_soundscape_pamflow_single_deployment(
#     sample_graphical_soundscape_parameters, sample_graphical_soundscape_output
# ):
#     """Test with single deployment."""
#     single_deployment_media = pd.DataFrame({
#         "mediaID": ["media_001", "media_002"],
#         "filePath": ["/path/to/file1.wav", "/path/to/file2.wav"],
#         "deploymentID": ["D1", "D1"],
#         "timestamp": pd.to_datetime([
#             "2024-01-01 08:30:00",
#             "2024-01-01 12:15:00",
#         ]),
#         "fileLength": [3600, 3600],
#     })
    
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = sample_graphical_soundscape_output
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             with patch("matplotlib.pyplot.close"):
#                 results = list(graphical_soundscape_pamflow(
#                     single_deployment_media, sample_graphical_soundscape_parameters
#                 ))
                
#                 # Should have 1 result
#                 assert len(results) == 1


# def test_graphical_soundscape_pamflow_preserves_dataframe_content(
#     sample_media, sample_graphical_soundscape_parameters, sample_graphical_soundscape_output
# ):
#     """Test that output DataFrame is unchanged from graphical_soundscape_maad."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = sample_graphical_soundscape_output
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             with patch("matplotlib.pyplot.close"):
#                 results = list(graphical_soundscape_pamflow(
#                     sample_media, sample_graphical_soundscape_parameters
#                 ))
                
#                 data_dict, _ = results[0]
                
#                 # Verify DataFrame content
#                 pd.testing.assert_frame_equal(
#                     data_dict["graph_D1"],
#                     sample_graphical_soundscape_output
#                 )


# def test_graphical_soundscape_pamflow_creates_subplots(
#     sample_media, sample_graphical_soundscape_parameters
# ):
#     """Test that subplots are created for each deployment."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = pd.DataFrame()
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             with patch("matplotlib.pyplot.close"):
#                 list(graphical_soundscape_pamflow(
#                     sample_media, sample_graphical_soundscape_parameters
#                 ))
                
#                 # subplots should be called twice (once per deployment)
#                 assert mock_subplots.call_count == 2


# def test_graphical_soundscape_pamflow_verbose_false(
#     sample_media, sample_graphical_soundscape_parameters
# ):
#     """Test that verbose=False is passed to graphical_soundscape_maad."""
#     with patch(
#         "pamflow.pipelines.graphical_soundscape.nodes.graphical_soundscape_maad"
#     ) as mock_gs:
#         mock_gs.return_value = pd.DataFrame()
        
#         with patch("matplotlib.pyplot.subplots") as mock_subplots:
#             mock_fig, mock_ax = MagicMock(), MagicMock()
#             mock_subplots.return_value = (mock_fig, mock_ax)
            
#             with patch("matplotlib.pyplot.close"):
#                 list(graphical_soundscape_pamflow(
#                     sample_media, sample_graphical_soundscape_parameters
#                 ))
                
#                 # Check that verbose=False was passed
#                 _, kwargs = mock_gs.call_args_list[0]
#                 assert kwargs.get("verbose") == False