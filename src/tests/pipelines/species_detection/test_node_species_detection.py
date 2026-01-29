# import pandas as pd
# import pytest
# from unittest.mock import patch, MagicMock

# from pamflow.pipelines.species_detection.nodes import species_detection_parallel


# @pytest.fixture
# def sample_media():
#     return pd.DataFrame(
#         {
#             "mediaID": [1, 2],
#             "deploymentID": ["D1", "D1"],
#             "filePath": ["file1.wav", "file2.wav"],
#         }
#     )


# @pytest.fixture
# def sample_deployments():
#     return pd.DataFrame(
#         {
#             "deploymentID": ["D1"],
#             "latitude": [10.0],
#             "longitude": [-84.0],
#         }
#     )


# def test_species_detection_parallel_simple(sample_media, sample_deployments):
#     """Simpler test that avoids multiprocessing entirely."""
    
#     mock_results = [
#         {
#             "common_name": "frog",
#             "scientific_name": "Lithobates sp.",
#             "start_time": 0.0,
#             "end_time": 1.0,
#             "confidence": 0.95,
#             "label": "frog_call",
#             "mediaID": 1,
#             "deploymentID": "D1",
#             "latitude": 10.0,
#             "longitude": -84.0,
#         },
#     ]
    
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file",
#         return_value=mock_results
#     ):
#         result = species_detection_parallel(
#             media=sample_media,
#             deployments=sample_deployments,
#             n_jobs=1,
#         )
    
#     assert isinstance(result, pd.DataFrame)
#     assert "scientificName" in result.columns


# --------------- OTHER TESTS FOR SPECIES DETECTION PIPELINE NODE ---------------
# import pytest
# from unittest.mock import Mock, MagicMock, patch, call
# import pandas as pd
# import numpy as np
# import logging
# from pamflow.pipelines.species_detection.nodes import species_detection_parallel


# @pytest.fixture
# def sample_media():
#     """Create sample media DataFrame."""
#     return pd.DataFrame({
#         "mediaID": ["media_001", "media_002", "media_003"],
#         "filePath": [
#             "/path/to/file1.wav",
#             "/path/to/file2.wav",
#             "/path/to/file3.wav"
#         ],
#         "deploymentID": ["sensor1", "sensor2", "sensor1"],
#         "timestamp": pd.to_datetime([
#             "2024-01-01 10:00:00",
#             "2024-01-02 12:00:00",
#             "2024-01-03 14:00:00"
#         ]),
#         "fileLength": [3600, 7200, 5400]
#     })


# @pytest.fixture
# def sample_deployments():
#     """Create sample deployments DataFrame."""
#     return pd.DataFrame({
#         "deploymentID": ["sensor1", "sensor2"],
#         "latitude": [40.7128, 34.0522],
#         "longitude": [-74.0060, -118.2437]
#     })


# @pytest.fixture
# def mock_detection_result():
#     """Create a mock detection result with proper structure."""
#     return [
#         {
#             "scientific_name": "Canis lupus",
#             "common_name": "Gray Wolf",
#             "start_time": 10.5,
#             "end_time": 15.3,
#             "confidence": 0.92,
#             "label": "GREY_WOLF",
#             "mediaID": "media_001",
#             "deploymentID": "sensor1",
#             "latitude": 40.7128,
#             "longitude": -74.0060
#         },
#         {
#             "scientific_name": "Canis lupus",
#             "common_name": "Gray Wolf",
#             "start_time": 22.1,
#             "end_time": 28.7,
#             "confidence": 0.87,
#             "label": "GREY_WOLF",
#             "mediaID": "media_001",
#             "deploymentID": "sensor1",
#             "latitude": 40.7128,
#             "longitude": -74.0060
#         }
#     ]


# def test_species_detection_parallel_returns_dataframe(sample_media, sample_deployments):
#     """Test that species_detection_parallel returns a pandas DataFrame."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = []
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         assert isinstance(result, pd.DataFrame)


# def test_species_detection_parallel_merges_data(sample_media, sample_deployments):
#     """Test that media and deployments are merged correctly."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = []
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         # Verify detection was called for each media file
#         assert mock_detection.call_count == len(sample_media)


# def test_species_detection_parallel_column_renaming(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that columns are renamed correctly."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         # Verify renamed columns exist
#         assert "scientificName" in result.columns
#         assert "eventStart" in result.columns
#         assert "eventEnd" in result.columns
#         assert "classificationProbability" in result.columns
        
#         # Verify old columns are removed
#         assert "scientific_name" not in result.columns
#         assert "start_time" not in result.columns
#         assert "end_time" not in result.columns
#         assert "confidence" not in result.columns


# def test_species_detection_parallel_adds_required_columns(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that required columns are added to the output."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         # Verify required columns are present
#         required_columns = [
#             "observationID", "eventID", "observationLevel", "observationType",
#             "count", "lifeStage", "sex", "behavior", "individualID",
#             "individualPositionRadius", "frequencyLow", "frequencyHigh",
#             "classificationMethod", "classificationTimestamp",
#             "observationTags", "observationComments"
#         ]
#         for col in required_columns:
#             assert col in result.columns


# def test_species_detection_parallel_sets_classification_method_machine(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that classificationMethod is set to 'machine'."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         assert (result["classificationMethod"] == "machine").all()


# def test_species_detection_parallel_classification_probability_rounded(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that classification probability is rounded to 3 decimal places."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         # Verify probabilities are rounded to 3 decimals
#         for prob in result["classificationProbability"]:
#             # Check decimal places
#             decimal_str = str(prob).split(".")[-1] if "." in str(prob) else "0"
#             assert len(decimal_str) <= 3


# def test_species_detection_parallel_drops_unwanted_columns(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that common_name and label columns are dropped."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         assert "common_name" not in result.columns
#         assert "label" not in result.columns


# def test_species_detection_parallel_observation_id_assignment(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that observationID is assigned as index."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         # observationID should be equal to the index
#         assert (result["observationID"] == result.index).all()


# def test_species_detection_parallel_event_id_none(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that eventID is set to None initially."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         assert result["eventID"].isna().all()


# def test_species_detection_parallel_empty_results(sample_media, sample_deployments):
#     """Test handling of empty detection results."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = []
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         assert isinstance(result, pd.DataFrame)
#         assert len(result) == 0


# def test_species_detection_parallel_observation_level_interval(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that observationLevel is set to 'interval'."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         assert (result["observationLevel"] == "interval").all()


# def test_species_detection_parallel_observation_type_animal(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that observationType is set to 'animal'."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         assert (result["observationType"] == "animal").all()


# def test_species_detection_parallel_multiple_detections_per_file(sample_media, sample_deployments):
#     """Test handling of multiple detections per file."""
#     detection_results = [
#         [
#             {
#                 "scientific_name": "Species A",
#                 "common_name": "Common A",
#                 "start_time": 10.0,
#                 "end_time": 15.0,
#                 "confidence": 0.95,
#                 "label": "A",
#                 "mediaID": "media_001",
#                 "deploymentID": "sensor1",
#                 "latitude": 40.7128,
#                 "longitude": -74.0060
#             }
#         ],
#         [
#             {
#                 "scientific_name": "Species B",
#                 "common_name": "Common B",
#                 "start_time": 20.0,
#                 "end_time": 25.0,
#                 "confidence": 0.88,
#                 "label": "B",
#                 "mediaID": "media_002",
#                 "deploymentID": "sensor2",
#                 "latitude": 34.0522,
#                 "longitude": -118.2437
#             }
#         ],
#         []
#     ]
    
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.side_effect = detection_results
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         assert len(result) == 2
#         assert "scientificName" in result.columns


# def test_species_detection_parallel_calls_detection_with_correct_args(
#     sample_media, sample_deployments
# ):
#     """Test that species_detection_single_file is called with correct arguments."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = []
        
#         species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         # Verify calls were made with correct parameters
#         calls = mock_detection.call_args_list
#         assert len(calls) == 3


# def test_species_detection_parallel_geographic_metadata_preserved(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that latitude and longitude are preserved in results."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         assert "latitude" in result.columns
#         assert "longitude" in result.columns
#         assert (result["latitude"] == 40.7128).all()
#         assert (result["longitude"] == -74.0060).all()


# def test_species_detection_parallel_all_null_columns_initialized(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that null columns are properly initialized."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         # These columns should be NaN/None
#         assert result["eventID"].isna().all()
#         assert result["lifeStage"].isna().all()
#         assert result["sex"].isna().all()
#         assert result["behavior"].isna().all()


# def test_species_detection_parallel_count_is_one(
#     sample_media, sample_deployments, mock_detection_result
# ):
#     """Test that count column is set to 1."""
#     with patch(
#         "pamflow.pipelines.species_detection.nodes.species_detection_single_file"
#     ) as mock_detection:
#         mock_detection.return_value = mock_detection_result
        
#         result = species_detection_parallel(sample_media, sample_deployments, n_jobs=1)
        
#         assert (result["count"] == 1).all()
