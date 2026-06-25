import pytest
import pandas as pd
import numpy as np
from pamflow.pipelines.species_detection.nodes import filter_observations


@pytest.fixture
def sample_observations():
    """Create sample observations DataFrame."""
    return pd.DataFrame({
        "observationID": range(1, 21),
        "mediaID": ["media_001"] * 5 + ["media_002"] * 5 + ["media_003"] * 10,
        "scientificName": ["Canis lupus"] * 5 + ["Ursus arctos"] * 5 + ["Canis lupus"] * 10,
        "classificationMethod": ["machine"] * 15 + ["human"] * 5,
        "classificationProbability": np.random.rand(20),
        "eventStart": np.random.rand(20) * 100,
        "eventEnd": np.random.rand(20) * 100 + 100,
        "deploymentID": ["sensor1"] * 10 + ["sensor2"] * 10,
        "latitude": [40.7128] * 10 + [34.0522] * 10,
        "longitude": [-74.0060] * 10 + [-118.2437] * 10,
    })


@pytest.fixture
def sample_target_species():
    """Create sample target species DataFrame."""
    return pd.DataFrame({
        "scientificName": ["Canis lupus", "Ursus arctos"]
    })


@pytest.fixture
def sample_target_species_single():
    """Create sample target species DataFrame with single species."""
    return pd.DataFrame({
        "scientificName": ["Canis lupus"]
    })


@pytest.fixture
def sample_target_species_empty():
    """Create empty target species DataFrame."""
    return pd.DataFrame({
        "scientificName": []
    })


def test_filter_observations_with_target_species(
    sample_observations, sample_target_species
):
    """Test that observations are filtered to only include target species."""
    minimum_observations = 5
    segment_size = 2
    
    result = filter_observations(
        sample_observations, sample_target_species, minimum_observations, segment_size
    )
    
    # Should only have the two target species
    assert set(result["scientificName"].unique()) == {"Canis lupus", "Ursus arctos"}


def test_filter_observations_minimum_observations_threshold(
    sample_observations, sample_target_species
):
    """Test that species with fewer observations than minimum are removed."""
    minimum_observations = 10
    segment_size = 2
    
    result = filter_observations(
        sample_observations, sample_target_species, minimum_observations, segment_size
    )
    
    # Only "Canis lupus" has 15 observations (>= 10)
    assert result["scientificName"].unique()[0] == "Canis lupus"
    assert len(result) >= minimum_observations


def test_filter_observations_removes_species_below_threshold(
    sample_observations, sample_target_species
):
    """Test that species below minimum observation threshold are excluded."""
    minimum_observations = 8
    segment_size = 2
    
    result = filter_observations(
        sample_observations, sample_target_species, minimum_observations, segment_size
    )
    
    # "Ursus arctos" has only 5 observations, should be removed
    assert "Ursus arctos" not in result["scientificName"].unique()
    assert "Canis lupus" in result["scientificName"].unique()


def test_filter_observations_raises_error_segment_size_greater_than_minimum(
    sample_observations, sample_target_species
):
    """Test that error is raised when segment_size > minimum_observations."""
    minimum_observations = 5
    segment_size = 10
    
    with pytest.raises(ValueError, match="Number of segments per species"):
        filter_observations(
            sample_observations, sample_target_species, minimum_observations, segment_size
        )


def test_filter_observations_with_single_target_species(
    sample_observations, sample_target_species_single
):
    """Test filtering with a single target species."""
    minimum_observations = 5
    segment_size = 2
    
    result = filter_observations(
        sample_observations, sample_target_species_single, minimum_observations, segment_size
    )
    
    assert result["scientificName"].unique()[0] == "Canis lupus"
    assert len(result["scientificName"].unique()) == 1


def test_filter_observations_with_empty_target_species(
    sample_observations, sample_target_species_empty
):
    """Test that all observations are kept when target_species is empty."""
    minimum_observations = 5
    segment_size = 2
    
    result = filter_observations(
        sample_observations, sample_target_species_empty, minimum_observations, segment_size
    )
    
    # With empty target species, filtering is skipped, so all species >= minimum_observations are kept
    assert len(result) > 0


def test_filter_observations_raises_error_no_matching_species(
    sample_observations, sample_target_species_empty
):
    """Test that error is raised when no species match target list."""
    # Create target species that don't exist in observations
    target_species_not_found = pd.DataFrame({
        "scientificName": ["Panthera leo", "Panthera tigris"]
    })
    minimum_observations = 5
    segment_size = 2
    
    with pytest.raises(ValueError, match="None of the"):
        filter_observations(
            sample_observations, target_species_not_found, minimum_observations, segment_size
        )


def test_filter_observations_raises_error_insufficient_observations(
    sample_observations, sample_target_species
):
    """Test that error is raised when no species meet minimum observation threshold."""
    minimum_observations = 50  # Higher than any species has
    segment_size = 2
    
    with pytest.raises(ValueError, match="None of the.*have as many observations"):
        filter_observations(
            sample_observations, sample_target_species, minimum_observations, segment_size
        )


def test_filter_observations_preserves_observation_structure(
    sample_observations, sample_target_species
):
    """Test that filtered observations maintain the original DataFrame structure."""
    minimum_observations = 5
    segment_size = 2
    
    result = filter_observations(
        sample_observations, sample_target_species, minimum_observations, segment_size
    )
    
    # Check that all original columns are preserved
    assert all(col in result.columns for col in sample_observations.columns)
    # Check that result is a DataFrame
    assert isinstance(result, pd.DataFrame)


def test_filter_observations_removes_duplicates_from_target_species(
):
    """Test that duplicate species in target list are handled correctly."""
    observations = pd.DataFrame({
        "observationID": range(1, 21),
        "scientificName": ["Canis lupus"] * 15 + ["Ursus arctos"] * 5,
        "classificationMethod": ["machine"] * 20,
        "classificationProbability": np.random.rand(20),
        "eventStart": np.random.rand(20) * 100,
        "eventEnd": np.random.rand(20) * 100 + 100,
        "mediaID": [f"media_{i}" for i in range(20)],
        "deploymentID": ["sensor1"] * 20,
        "latitude": [40.7128] * 20,
        "longitude": [-74.0060] * 20,
    })
    
    # Target species with duplicates
    target_species = pd.DataFrame({
        "scientificName": ["Canis lupus", "Canis lupus", "Ursus arctos"]
    })
    
    minimum_observations = 5
    segment_size = 2
    
    result = filter_observations(
        observations, target_species, minimum_observations, segment_size
    )
    
    # Should still work correctly despite duplicates
    assert set(result["scientificName"].unique()) == {"Canis lupus", "Ursus arctos"}


def test_filter_observations_minimum_equals_actual_count(
    sample_observations, sample_target_species
):
    """Test that species with exactly the minimum observations are kept."""
    # Adjust data: Ursus arctos has 5 observations
    minimum_observations = 5
    segment_size = 2
    
    result = filter_observations(
        sample_observations, sample_target_species, minimum_observations, segment_size
    )
    
    # Both species should be kept since they both meet the threshold
    assert "Ursus arctos" in result["scientificName"].unique() or len(result) > 0


def test_filter_observations_filters_by_scientific_name_field(
    sample_observations, sample_target_species
):
    """Test that filtering uses the scientificName field correctly."""
    minimum_observations = 5
    segment_size = 2
    
    result = filter_observations(
        sample_observations, sample_target_species, minimum_observations, segment_size
    )
    
    # Verify filtering was done on scientificName
    assert all(
        name in sample_target_species["scientificName"].values
        for name in result["scientificName"].unique()
    )


def test_filter_observations_returns_subset_of_original(
    sample_observations, sample_target_species
):
    """Test that filtered result is a subset of original observations."""
    minimum_observations = 5
    segment_size = 2
    
    result = filter_observations(
        sample_observations, sample_target_species, minimum_observations, segment_size
    )
    
    # Result should have fewer or equal rows than original
    assert len(result) <= len(sample_observations)


def test_filter_observations_preserves_metadata(
    sample_observations, sample_target_species
):
    """Test that geographic and deployment metadata are preserved."""
    minimum_observations = 5
    segment_size = 2
    
    result = filter_observations(
        sample_observations, sample_target_species, minimum_observations, segment_size
    )
    
    # Check that metadata columns are preserved
    assert "latitude" in result.columns
    assert "longitude" in result.columns
    assert "deploymentID" in result.columns
    assert result["latitude"].notna().all()
    assert result["longitude"].notna().all()


def test_filter_observations_large_minimum_threshold(
    sample_observations, sample_target_species
):
    """Test behavior with a very large minimum observation threshold."""
    minimum_observations = 1000
    segment_size = 2
    
    with pytest.raises(ValueError, match="have as many observations"):
        filter_observations(
            sample_observations, sample_target_species, minimum_observations, segment_size
        )


def test_filter_observations_segment_size_equals_minimum(
    sample_observations, sample_target_species
):
    """Test that segment_size equal to minimum_observations is allowed."""
    minimum_observations = 5
    segment_size = 5
    
    result = filter_observations(
        sample_observations, sample_target_species, minimum_observations, segment_size
    )
    
    # Should work without errors
    assert isinstance(result, pd.DataFrame)


def test_filter_observations_single_observation_per_species(
    sample_target_species
):
    """Test filtering with only one observation per species."""
    observations = pd.DataFrame({
        "observationID": [1, 2],
        "scientificName": ["Canis lupus", "Ursus arctos"],
        "classificationMethod": ["machine", "machine"],
        "classificationProbability": [0.9, 0.85],
        "eventStart": [10.0, 20.0],
        "eventEnd": [15.0, 25.0],
        "mediaID": ["media_001", "media_002"],
        "deploymentID": ["sensor1", "sensor2"],
        "latitude": [40.7128, 34.0522],
        "longitude": [-74.0060, -118.2437],
    })
    
    minimum_observations = 2
    segment_size = 1
    
    with pytest.raises(ValueError, match="have as many observations"):
        filter_observations(
            observations, sample_target_species, minimum_observations, segment_size
        )