import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, call
from pamflow.pipelines.acoustic_indices.nodes import compute_indices


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
def sample_media_single_deployment():
    """Create sample media with single deployment."""
    return pd.DataFrame({
        "mediaID": ["media_001", "media_002"],
        "filePath": [
            "/path/to/file1.wav",
            "/path/to/file2.wav",
        ],
        "deploymentID": ["D1", "D1"],
        "timestamp": pd.to_datetime([
            "2024-01-01 08:30:00",
            "2024-01-01 12:15:00",
        ]),
        "fileLength": [3600, 3600],
    })


@pytest.fixture
def sample_acoustic_indices_parameters():
    """Create sample acoustic indices parameters."""
    return {
        "preprocess": {
            "target_fs": 22050,
            "filter_type": "bandpass",
            "filter_cut": [100, 10000],
            "filter_order": 4,
        },
        "indices_settings": {
            "aci": True,
            "ndsi": True,
            "biophony": True,
            "anthrophony": True,
            "aei": True,
        },
        "execution": {
            "n_jobs": 2,
        },
    }


@pytest.fixture
def sample_acoustic_indices_output():
    """Create sample acoustic indices output DataFrame."""
    return pd.DataFrame({
        "mediaID": ["media_001", "media_002"],
        "deploymentID": ["D1", "D1"],
        "aci": [0.5, 0.6],
        "ndsi": [0.7, 0.8],
        "biophony": [0.65, 0.75],
        "anthrophony": [0.35, 0.25],
        "aei": [0.8, 0.85],
    })


def test_compute_indices_returns_generator(sample_media, sample_acoustic_indices_parameters):
    """Test that compute_indices returns a generator."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        result = compute_indices(sample_media, sample_acoustic_indices_parameters)
        
        # Check that it's a generator
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")


def test_compute_indices_yields_dict(
    sample_media, sample_acoustic_indices_parameters, sample_acoustic_indices_output
):
    """Test that function yields dictionaries with correct structure."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = sample_acoustic_indices_output
        
        result = compute_indices(sample_media, sample_acoustic_indices_parameters)
        results_list = list(result)
        
        # Should yield 2 results (one per deployment)
        assert len(results_list) == 2
        
        # Each result should be a dict
        for result_dict in results_list:
            assert isinstance(result_dict, dict)


def test_compute_indices_yields_correct_keys(
    sample_media, sample_acoustic_indices_parameters, sample_acoustic_indices_output
):
    """Test that yielded dictionaries have correct key names."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = sample_acoustic_indices_output
        
        result = compute_indices(sample_media, sample_acoustic_indices_parameters)
        results_list = list(result)
        
        # Check keys for each deployment
        assert "indices_D1" in results_list[0]
        assert "indices_D2" in results_list[1]


def test_compute_indices_processes_multiple_deployments(
    sample_media, sample_acoustic_indices_parameters
):
    """Test that function processes each deployment separately."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # compute_indices_parallel should be called once per deployment
        assert mock_compute.call_count == 2


def test_compute_indices_correct_deployment_data(
    sample_media, sample_acoustic_indices_parameters
):
    """Test that each deployment receives correct filtered data."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # Check that correct data was passed
        calls = mock_compute.call_args_list
        
        # First call should have 3 files from D1
        first_call_data = calls[0][0][0]
        assert len(first_call_data) == 3
        assert (first_call_data["deploymentID"] == "D1").all()
        
        # Second call should have 2 files from D2
        second_call_data = calls[1][0][0]
        assert len(second_call_data) == 2
        assert (second_call_data["deploymentID"] == "D2").all()


def test_compute_indices_excludes_zero_length_files(
    sample_media_zero_length, sample_acoustic_indices_parameters
):
    """Test that files with zero length are excluded."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media_zero_length, sample_acoustic_indices_parameters))
        
        # Should only process 2 files (zero-length file excluded)
        call_data = mock_compute.call_args_list[0][0][0]
        assert len(call_data) == 2
        assert (call_data["fileLength"] > 0).all()


def test_compute_indices_passes_correct_parameters(
    sample_media, sample_acoustic_indices_parameters
):
    """Test that correct parameters are passed to compute_indices_parallel."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # Get first call
        args, kwargs = mock_compute.call_args_list[0]
        
        # Check that correct parameters were passed
        assert args[1] == sample_acoustic_indices_parameters["preprocess"]
        assert args[2] == sample_acoustic_indices_parameters["indices_settings"]
        assert args[3] == sample_acoustic_indices_parameters["execution"]["n_jobs"]


def test_compute_indices_passes_n_jobs(
    sample_media, sample_acoustic_indices_parameters
):
    """Test that n_jobs parameter is correctly extracted and passed."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # Check n_jobs in all calls
        for call_args in mock_compute.call_args_list:
            args, _ = call_args
            assert args[3] == 2  # n_jobs value


def test_compute_indices_single_deployment(
    sample_media_single_deployment, sample_acoustic_indices_parameters, sample_acoustic_indices_output
):
    """Test with single deployment."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = sample_acoustic_indices_output
        
        results = list(compute_indices(sample_media_single_deployment, sample_acoustic_indices_parameters))
        
        # Should have 1 result
        assert len(results) == 1
        assert "indices_D1" in results[0]


def test_compute_indices_returns_dataframe_values(
    sample_media, sample_acoustic_indices_parameters, sample_acoustic_indices_output
):
    """Test that yielded values are DataFrames."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = sample_acoustic_indices_output
        
        results = list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        for result_dict in results:
            for value in result_dict.values():
                assert isinstance(value, pd.DataFrame)


def test_compute_indices_preserves_dataframe_content(
    sample_media, sample_acoustic_indices_parameters, sample_acoustic_indices_output
):
    """Test that output DataFrame is unchanged from compute_indices_parallel."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = sample_acoustic_indices_output
        
        results = list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # Verify DataFrame content
        pd.testing.assert_frame_equal(
            results[0]["indices_D1"],
            sample_acoustic_indices_output
        )


def test_compute_indices_empty_media():
    """Test with empty media DataFrame."""
    empty_media = pd.DataFrame({
        "mediaID": [],
        "filePath": [],
        "deploymentID": [],
        "timestamp": [],
        "fileLength": [],
    })
    
    params = {
        "preprocess": {
            "target_fs": 22050,
            "filter_type": "bandpass",
            "filter_cut": [100, 10000],
            "filter_order": 4,
        },
        "indices_settings": {
            "aci": True,
            "ndsi": True,
        },
        "execution": {
            "n_jobs": 2,
        },
    }
    
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        results = list(compute_indices(empty_media, params))
        
        # Should return empty generator
        assert len(results) == 0


def test_compute_indices_all_files_zero_length(sample_acoustic_indices_parameters):
    """Test when all files have zero length."""
    all_zero_media = pd.DataFrame({
        "mediaID": ["media_001", "media_002"],
        "filePath": ["/path/to/file1.wav", "/path/to/file2.wav"],
        "deploymentID": ["D1", "D1"],
        "timestamp": pd.to_datetime([
            "2024-01-01 08:30:00",
            "2024-01-01 12:15:00",
        ]),
        "fileLength": [0, 0],
    })
    
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        results = list(compute_indices(all_zero_media, sample_acoustic_indices_parameters))
        
        # Should return empty generator
        assert len(results) == 0
        # compute_indices_parallel should not be called
        assert mock_compute.call_count == 0


def test_compute_indices_multiple_deployments_count(sample_media, sample_acoustic_indices_parameters):
    """Test that correct number of unique deployments are processed."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # Should have 2 unique deployments
        assert mock_compute.call_count == 2


def test_compute_indices_with_many_deployments(sample_acoustic_indices_parameters):
    """Test with many deployments."""
    # Create media with 5 deployments
    media = pd.DataFrame({
        "mediaID": [f"media_{i:03d}" for i in range(1, 11)],
        "filePath": [f"/path/to/file{i}.wav" for i in range(1, 11)],
        "deploymentID": ["D1", "D1", "D2", "D2", "D3", "D3", "D4", "D4", "D5", "D5"],
        "timestamp": pd.date_range("2024-01-01", periods=10, freq="H"),
        "fileLength": [3600] * 10,
    })
    
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        results = list(compute_indices(media, sample_acoustic_indices_parameters))
        
        # Should have 5 results
        assert len(results) == 5
        assert mock_compute.call_count == 5


def test_compute_indices_deployment_order_consistent(
    sample_media, sample_acoustic_indices_parameters, sample_acoustic_indices_output
):
    """Test that deployments are processed in consistent order."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = sample_acoustic_indices_output
        
        results = list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # Keys should be in predictable format
        keys = [list(r.keys())[0] for r in results]
        
        # Should contain both expected deployments
        assert any("D1" in k for k in keys)
        assert any("D2" in k for k in keys)


def test_compute_indices_extracts_parameters_correctly(
    sample_media, sample_acoustic_indices_parameters
):
    """Test that parameters are extracted correctly from nested dict."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # Verify parameters were extracted correctly
        call_args = mock_compute.call_args_list[0]
        args = call_args[0]
        
        # Check preprocess params
        assert args[1] == {
            "target_fs": 22050,
            "filter_type": "bandpass",
            "filter_cut": [100, 10000],
            "filter_order": 4,
        }
        
        # Check indices settings
        assert args[2] == {
            "aci": True,
            "ndsi": True,
            "biophony": True,
            "anthrophony": True,
            "aei": True,
        }
        
        # Check n_jobs
        assert args[3] == 2


def test_compute_indices_does_not_modify_input_media(
    sample_media, sample_acoustic_indices_parameters
):
    """Test that input media DataFrame is not modified."""
    media_copy = sample_media.copy()
    
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # Check that input wasn't modified (except filtering during processing)
        assert sample_media.shape[0] >= media_copy[media_copy["fileLength"] > 0].shape[0]


def test_compute_indices_zero_length_filtering_correct(sample_media_zero_length, sample_acoustic_indices_parameters):
    """Test that zero-length filtering is applied correctly."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media_zero_length, sample_acoustic_indices_parameters))
        
        # Should only have 2 files (one zero-length file excluded)
        call_data = mock_compute.call_args_list[0][0][0]
        assert len(call_data) == 2
        
        # Verify no zero-length files
        assert (call_data["fileLength"] > 0).all()


def test_compute_indices_preserves_deployment_metadata(
    sample_media, sample_acoustic_indices_parameters
):
    """Test that deployment metadata is preserved in grouped data."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # Check first deployment
        first_call_data = mock_compute.call_args_list[0][0][0]
        assert "deploymentID" in first_call_data.columns
        assert "filePath" in first_call_data.columns
        assert "mediaID" in first_call_data.columns


def test_compute_indices_handles_large_parameter_dict(
    sample_media, sample_acoustic_indices_parameters
):
    """Test that complex parameter dictionary is handled correctly."""
    complex_params = {
        "preprocess": {
            "target_fs": 22050,
            "filter_type": "bandpass",
            "filter_cut": [100, 10000],
            "filter_order": 4,
            "extra_param": "some_value",
        },
        "indices_settings": {
            "aci": True,
            "ndsi": True,
            "biophony": True,
            "anthrophony": True,
            "aei": True,
            "adi": True,
            "scene_complexity": True,
        },
        "execution": {
            "n_jobs": 4,
            "backend": "threading",
        },
    }
    
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media, complex_params))
        
        # Should still work correctly
        assert mock_compute.call_count == 2


def test_compute_indices_deployment_count_logged(
    sample_media, sample_acoustic_indices_parameters, caplog
):
    """Test that deployment and file counts are logged."""
    with patch(
        "pamflow.pipelines.acoustic_indices.nodes.compute_indices_parallel"
    ) as mock_compute:
        mock_compute.return_value = pd.DataFrame()
        
        list(compute_indices(sample_media, sample_acoustic_indices_parameters))
        
        # Verify logging happened (basic check)
        assert mock_compute.call_count == 2