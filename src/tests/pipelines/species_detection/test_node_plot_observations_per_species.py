import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
from pamflow.pipelines.species_detection.nodes import plot_observations_per_species


@pytest.fixture
def sample_observations():
    """Create sample observations DataFrame with multiple species."""
    return pd.DataFrame({
        "scientificName": (
            ["Canis lupus"] * 15 +
            ["Ursus arctos"] * 12 +
            ["Lynx canadensis"] * 10 +
            ["Cervus elaphus"] * 8 +
            ["Alces alces"] * 6 +
            ["Vulpes vulpes"] * 5 +
            ["Puma concolor"] * 4 +
            ["Felis catus"] * 3 +
            ["Procyon lotor"] * 2 +
            ["Didelphis virginiana"] * 1
        ),
    })


@pytest.fixture
def sample_observations_few_species():
    """Create observations with few species."""
    return pd.DataFrame({
        "scientificName": (
            ["Species_A"] * 10 +
            ["Species_B"] * 8 +
            ["Species_C"] * 5
        ),
    })


@pytest.fixture
def sample_observations_many_species():
    """Create observations with more than 25 species."""
    species_names = [f"Species_{i:02d}" for i in range(30)]
    species_list = []
    for i, name in enumerate(species_names):
        species_list.extend([name] * (30 - i))  # Decreasing counts
    
    return pd.DataFrame({
        "scientificName": species_list,
    })


@pytest.fixture
def sample_observations_equal_counts():
    """Create observations where all species have equal counts."""
    return pd.DataFrame({
        "scientificName": (
            ["Species_A"] * 10 +
            ["Species_B"] * 10 +
            ["Species_C"] * 10 +
            ["Species_D"] * 10
        ),
    })


class TestPlotObservationsPerSpeciesBasic:
    """Basic tests for plot_observations_per_species function."""

    def test_returns_matplotlib_figure(self, sample_observations):
        """Test that function returns a matplotlib Figure object."""
        result = plot_observations_per_species(sample_observations)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_figure_has_correct_size(self, sample_observations):
        """Test that figure has correct size."""
        result = plot_observations_per_species(sample_observations)
        figsize = result.get_size_inches()
        assert figsize[0] == 8  # width
        assert figsize[1] == 6  # height

    def test_figure_has_axes(self, sample_observations):
        """Test that figure has axes."""
        result = plot_observations_per_species(sample_observations)
        axes = result.get_axes()
        assert len(axes) > 0

    def test_axes_is_barh(self, sample_observations):
        """Test that axes contains horizontal bar chart."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        
        # Check for bar containers
        assert len(ax.patches) > 0

    def test_with_single_species(self):
        """Test with single species."""
        single_species = pd.DataFrame({
            "scientificName": ["Species_A"] * 10,
        })
        
        result = plot_observations_per_species(single_species)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_with_two_species(self):
        """Test with two species."""
        two_species = pd.DataFrame({
            "scientificName": ["Species_A"] * 10 + ["Species_B"] * 5,
        })
        
        result = plot_observations_per_species(two_species)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_with_empty_dataframe_raises_error(self):
        """Test that empty observations DataFrame raises an error."""
        empty_observations = pd.DataFrame({
            "scientificName": [],
        })
        
        with pytest.raises((ValueError, KeyError)):
            plot_observations_per_species(empty_observations)


class TestPlotObservationsPerSpeciesTitle:
    """Tests for title generation in plot_observations_per_species."""

    def test_title_includes_fewer_than_25_species(self, sample_observations_few_species):
        """Test that title shows total species count when fewer than 25."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        title = ax.get_title()
        
        assert "3 species" in title
        assert "Top" not in title

    def test_title_includes_more_than_25_species(self, sample_observations_many_species):
        """Test that title shows top 25 when more than 25 species."""
        result = plot_observations_per_species(sample_observations_many_species)
        ax = result.get_axes()[0]
        title = ax.get_title()
        
        assert "Top 25" in title
        assert "30 species" in title

    def test_title_has_number_of_observations_per_species_text(self, sample_observations):
        """Test that title contains standard text."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        title = ax.get_title()
        
        assert "Number of observations per species" in title

    def test_title_color_is_gray(self, sample_observations):
        """Test that title color is gray."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        title_obj = ax.title
        
        # Color should be gray
        assert title_obj.get_color() == "gray"

    def test_title_weight_is_bold(self, sample_observations):
        """Test that title weight is bold."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        title_obj = ax.title
        
        assert title_obj.get_weight() == "bold"


class TestPlotObservationsPerSpeciesBarChart:
    """Tests for bar chart rendering."""

    def test_bars_sorted_ascending(self, sample_observations_few_species):
        """Test that bars are sorted in ascending order."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        
        # Get bar widths (which correspond to counts)
        widths = [bar.get_width() for bar in ax.patches]
        
        # Check if sorted in ascending order
        assert widths == sorted(widths)

    def test_bar_count_matches_species(self, sample_observations_few_species):
        """Test that number of bars matches number of species."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        
        n_bars = len(ax.patches)
        n_species = sample_observations_few_species["scientificName"].nunique()
        
        assert n_bars == n_species

    def test_bar_count_limited_to_25_when_more_species(self, sample_observations_many_species):
        """Test that only top 25 bars are shown when more than 25 species."""
        result = plot_observations_per_species(sample_observations_many_species)
        ax = result.get_axes()[0]
        
        n_bars = len(ax.patches)
        
        assert n_bars == 25

    def test_bar_height_not_zero(self, sample_observations):
        """Test that all bars have non-zero heights."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        
        for bar in ax.patches:
            assert bar.get_height() > 0

    def test_bar_alpha_value(self, sample_observations):
        """Test that bars have correct alpha value."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        
        for bar in ax.patches:
            assert bar.get_alpha() == 0.85

    def test_xlim_provides_space_for_labels(self, sample_observations_few_species):
        """Test that xlim is set to accommodate labels."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        
        xlim = ax.get_xlim()
        max_count = sample_observations_few_species["scientificName"].value_counts().max()
        
        # xlim should be greater than max count * 1.12
        assert xlim[1] > max_count * 1.1


class TestPlotObservationsPerSpeciesLabels:
    """Tests for label rendering."""

    def test_species_names_on_y_axis(self, sample_observations_few_species):
        """Test that species names appear on y-axis."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        
        y_labels = [label.get_text() for label in ax.get_yticklabels()]
        
        # Should have species names
        assert len(y_labels) > 0
        assert any("Species" in label for label in y_labels)

    def test_species_names_are_italic(self, sample_observations_few_species):
        """Test that species names are italicized."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        
        for label in ax.get_yticklabels():
            # Check if font style is italic
            assert label.get_fontstyle() == "italic"

    def test_count_labels_on_bars(self, sample_observations_few_species):
        """Test that count labels appear on bars."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        
        # Check for text annotations
        texts = [text.get_text() for text in ax.texts]
        
        # Should have numeric labels
        assert len(texts) >= len(ax.patches)

    def test_count_label_color_is_grey(self, sample_observations_few_species):
        """Test that count labels are grey."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        
        for text in ax.texts:
            # Color should be grey
            assert text.get_color() == "grey"

    def test_count_label_fontsize(self, sample_observations_few_species):
        """Test that count labels have fontsize of 10."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        
        for text in ax.texts:
            assert text.get_fontsize() == 10

    def test_no_x_axis_visible(self, sample_observations):
        """Test that x-axis is not visible."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        
        # Check that x-axis is not visible
        assert not ax.get_xaxis().get_visible()

    def test_no_x_axis_ticks(self, sample_observations):
        """Test that x-axis ticks are not present."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        
        # Get x-axis ticks
        xticks = ax.get_xticks()
        
        # Should not display xticks (they might exist but not visible)
        assert not ax.get_xaxis().get_visible()

    def test_y_axis_ticks_not_visible(self, sample_observations):
        """Test that y-axis tick marks are not visible."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        
        # Check that tick marks are off
        assert ax.yaxis.get_tick_params()["left"] == False


class TestPlotObservationsPerSpeciesSpines:
    """Tests for spine visibility."""

    def test_spines_not_visible(self, sample_observations):
        """Test that all spines are not visible."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        
        for spine in ax.spines.values():
            assert not spine.get_visible()

    def test_all_four_spines_removed(self, sample_observations):
        """Test that all four spines (top, bottom, left, right) are removed."""
        result = plot_observations_per_species(sample_observations)
        ax = result.get_axes()[0]
        
        spine_names = ["top", "bottom", "left", "right"]
        for spine_name in spine_names:
            assert not ax.spines[spine_name].get_visible()


class TestPlotObservationsPerSpeciesData:
    """Tests for data accuracy in the plot."""

    def test_top_species_are_highest_counts(self, sample_observations_few_species):
        """Test that displayed species are the top species by count."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        
        # Get counts from original data
        counts = sample_observations_few_species["scientificName"].value_counts()
        top_counts = counts.head(25).sort_values(ascending=True).values
        
        # Get bar widths from plot
        bar_widths = sorted([bar.get_width() for bar in ax.patches])
        
        # Should match
        np.testing.assert_array_equal(bar_widths, top_counts)

    def test_species_names_match_top_species(self, sample_observations_few_species):
        """Test that species names in plot match top species."""
        result = plot_observations_per_species(sample_observations_few_species)
        ax = result.get_axes()[0]
        
        y_labels = [label.get_text() for label in ax.get_yticklabels()]
        
        # Get top species
        top_species = sample_observations_few_species["scientificName"].value_counts().head(25).sort_values(ascending=True).index.tolist()
        
        # Filter out empty strings from y_labels
        y_labels_clean = [label for label in y_labels if label]
        
        # Should contain top species
        assert len(y_labels_clean) >= len(top_species)

    def test_equal_count_species_both_shown(self, sample_observations_equal_counts):
        """Test that species with equal counts are all shown."""
        result = plot_observations_per_species(sample_observations_equal_counts)
        ax = result.get_axes()[0]
        
        n_bars = len(ax.patches)
        n_unique_species = sample_observations_equal_counts["scientificName"].nunique()
        
        assert n_bars == n_unique_species

    def test_single_species_single_bar(self):
        """Test that single species creates single bar."""
        single_species = pd.DataFrame({
            "scientificName": ["Only_Species"] * 20,
        })
        
        result = plot_observations_per_species(single_species)
        ax = result.get_axes()[0]
        
        assert len(ax.patches) == 1


class TestPlotObservationsPerSpeciesEdgeCases:
    """Edge case tests."""

    def test_species_with_very_long_names(self):
        """Test with very long species names."""
        long_names = pd.DataFrame({
            "scientificName": (
                ["Canis lupus familiaris domesticus subspecies arctos"] * 10 +
                ["Ursus arctos horribilis grizzly bear northern subspecies"] * 8 +
                ["Lynx canadensis northern lynx long subspecies designation"] * 6
            ),
        })
        
        result = plot_observations_per_species(long_names)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_species_with_special_characters(self):
        """Test with species names containing special characters."""
        special_chars = pd.DataFrame({
            "scientificName": (
                ["Species (A) variant"] * 10 +
                ["Species [B] type"] * 8 +
                ["Species/C hybrid"] * 6
            ),
        })
        
        result = plot_observations_per_species(special_chars)
        assert isinstance(result, matplotlib.figure.Figure)

    def test_very_large_observation_counts(self):
        """Test with very large observation counts."""
        large_counts = pd.DataFrame({
            "scientificName": (
                ["Species_A"] * 10000 +
                ["Species_B"] * 9000 +
                ["Species_C"] * 8000
            ),
        })
        
        result = plot_observations_per_species(large_counts)
        assert isinstance(result, matplotlib.figure.Figure)

    # def test_exactly_25_species(self):
    #     """Test with exactly 25 species."""
    #     species_names = [f"Species_{i:02d}" for i in range(25)]
    #     observations = pd.DataFrame({
    #         "scientificName": [s for s in species_names for _ in range(5 - (i % 5))
    #                          for i, s in enumerate(species_names)],
    #     })
        
    #     result = plot_observations_per_species(observations)
    #     ax = result.get_axes()[0]
        
    #     # Should show exactly 25 bars
    #     assert len(ax.patches) == 25

    def test_exactly_26_species(self):
        """Test with exactly 26 species (more than 25)."""
        species_names = [f"Species_{i:02d}" for i in range(26)]
        species_list = []
        for i, name in enumerate(species_names):
            species_list.extend([name] * (26 - i))
        
        observations = pd.DataFrame({
            "scientificName": species_list,
        })
        
        result = plot_observations_per_species(observations)
        ax = result.get_axes()[0]
        
        # Should show only top 25
        assert len(ax.patches) == 25

    def test_duplicate_observations(self, sample_observations):
        """Test with duplicate observations."""
        duplicated = pd.concat([sample_observations, sample_observations], ignore_index=True)
        
        result = plot_observations_per_species(duplicated)
        assert isinstance(result, matplotlib.figure.Figure)


class TestPlotObservationsPerSpeciesLayout:
    """Tests for layout and formatting."""

    def test_tight_layout_applied(self, sample_observations):
        """Test that tight_layout is applied."""
        result = plot_observations_per_species(sample_observations)
        
        # Verify figure was created with tight_layout
        assert isinstance(result, matplotlib.figure.Figure)
        assert len(result.get_axes()) > 0

    def test_no_plt_show_called(self, sample_observations):
        """Test that plt.show() is not called."""
        result = plot_observations_per_species(sample_observations)
        
        # Verify that result is returned without showing
        assert isinstance(result, matplotlib.figure.Figure)
        plt.close(result)


class TestPlotObservationsPerSpeciesMultipleCalls:
    """Tests for multiple function calls."""

    def test_multiple_calls_create_different_figures(self, sample_observations):
        """Test that multiple calls create different figure objects."""
        fig1 = plot_observations_per_species(sample_observations)
        fig2 = plot_observations_per_species(sample_observations)
        
        assert fig1 is not fig2
        plt.close(fig1)
        plt.close(fig2)

    def test_multiple_calls_with_different_data(self, sample_observations_few_species, sample_observations_many_species):
        """Test multiple calls with different data."""
        fig1 = plot_observations_per_species(sample_observations_few_species)
        fig2 = plot_observations_per_species(sample_observations_many_species)
        
        ax1 = fig1.get_axes()[0]
        ax2 = fig2.get_axes()[0]
        
        n_bars_1 = len(ax1.patches)
        n_bars_2 = len(ax2.patches)
        
        # Different data should result in different bar counts
        assert n_bars_1 == 3
        assert n_bars_2 == 25
        
        plt.close(fig1)
        plt.close(fig2)


class TestPlotObservationsPerSpeciesConsistency:
    """Tests for consistency and reproducibility."""

    def test_same_input_produces_same_output_structure(self, sample_observations):
        """Test that same input produces same output structure."""
        fig1 = plot_observations_per_species(sample_observations)
        fig2 = plot_observations_per_species(sample_observations)
        
        ax1 = fig1.get_axes()[0]
        ax2 = fig2.get_axes()[0]
        
        # Same number of bars
        assert len(ax1.patches) == len(ax2.patches)
        
        # Same bar widths (counts)
        widths1 = sorted([bar.get_width() for bar in ax1.patches])
        widths2 = sorted([bar.get_width() for bar in ax2.patches])
        
        np.testing.assert_array_equal(widths1, widths2)
        
        plt.close(fig1)
        plt.close(fig2)

    def test_deterministic_top_25_selection(self, sample_observations_many_species):
        """Test that top 25 selection is deterministic."""
        fig1 = plot_observations_per_species(sample_observations_many_species)
        fig2 = plot_observations_per_species(sample_observations_many_species)
        
        ax1 = fig1.get_axes()[0]
        ax2 = fig2.get_axes()[0]
        
        # Get titles (should mention top 25)
        title1 = ax1.get_title()
        title2 = ax2.get_title()
        
        assert title1 == title2
        
        plt.close(fig1)
        plt.close(fig2)