import pytest
from kedro.pipeline import Pipeline
from pamflow.pipelines.species_detection.pipeline import create_pipeline


class TestSpeciesDetectionPipeline:
    """Test suite for species detection pipeline."""

    def test_create_pipeline_returns_pipeline(self):
        """Test that create_pipeline returns a Pipeline object."""
        pipeline = create_pipeline()
        assert isinstance(pipeline, Pipeline)

    def test_pipeline_has_seven_nodes(self):
        """Test that pipeline contains exactly 7 nodes."""
        pipeline = create_pipeline()
        assert len(pipeline.nodes) == 7

    # def test_pipeline_node_names(self):
    #     """Test that all expected nodes exist."""
    #     pipeline = create_pipeline()
    #     node_names = [node.name for node in pipeline.nodes]
        
    #     expected_nodes = [
    #         "species_detection_node",
    #         "filter_observations_node",
    #         "create_segments_node",
    #         "create_segments_folder_node",
    #         "create_manual_annotation_formats_node",
    #         "plot_observations_summary_node",
    #         "plot_observations_per_species_node",
    #     ]
        
    #     assert node_names == expected_nodes

    def test_all_nodes_have_inputs(self):
        """Test that all nodes have inputs."""
        pipeline = create_pipeline()
        
        for node in pipeline.nodes:
            assert len(node.inputs) > 0

    def test_all_nodes_have_outputs(self):
        """Test that all nodes have outputs."""
        pipeline = create_pipeline()
        
        for node in pipeline.nodes:
            assert len(node.outputs) > 0

    def test_all_nodes_have_callable_functions(self):
        """Test that all nodes have callable functions."""
        pipeline = create_pipeline()
        
        for node in pipeline.nodes:
            assert callable(node.func)

    def test_species_detection_node_inputs(self):
        """Test species_detection_node inputs."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "species_detection_node"][0]
        
        expected_inputs = [
            "media@pamDP",
            "deployments@pamDP",
            "params:species_detection_parameters.n_jobs",
        ]
        
        assert list(node.inputs) == expected_inputs

    def test_species_detection_node_output(self):
        """Test species_detection_node output."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "species_detection_node"][0]
        
        assert node.outputs == ["unfiltered_observations@pamDP"]

    def test_filter_observations_node_inputs(self):
        """Test filter_observations_node inputs."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "filter_observations_node"][0]
        
        expected_inputs = [
            "unfiltered_observations@pamDP",
            "target_species@pandas",
            "params:species_detection_parameters.minimum_observations",
            "params:species_detection_parameters.segment_size",
        ]
        
        assert list(node.inputs) == expected_inputs

    def test_filter_observations_node_output(self):
        """Test filter_observations_node output."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "filter_observations_node"][0]
        
        assert node.outputs == ["observations@pamDP"]

    def test_create_segments_node_inputs(self):
        """Test create_segments_node inputs."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "create_segments_node"][0]
        
        expected_inputs = [
            "observations@pamDP",
            "media@pamDP",
            "params:species_detection_parameters.segment_size",
        ]
        
        assert list(node.inputs) == expected_inputs

    def test_create_segments_node_output(self):
        """Test create_segments_node output."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "create_segments_node"][0]
        
        assert node.outputs == ["segments@pandas"]

    def test_create_segments_folder_node_inputs(self):
        """Test create_segments_folder_node inputs."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "create_segments_folder_node"][0]
        
        expected_inputs = [
            "segments@pandas",
            "params:species_detection_parameters.n_jobs",
            "params:species_detection_parameters.segment_size",
        ]
        
        assert list(node.inputs) == expected_inputs

    def test_create_segments_folder_node_output(self):
        """Test create_segments_folder_node output."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "create_segments_folder_node"][0]
        
        assert node.outputs == ["segments_audio_folder@AudioFolderDataset"]

    def test_create_manual_annotation_formats_node_inputs(self):
        """Test create_manual_annotation_formats_node inputs."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "create_manual_annotation_formats_node"][0]
        
        expected_inputs = [
            "segments@pandas",
            "params:species_detection_parameters.manual_annotations_file_name",
        ]
        
        assert list(node.inputs) == expected_inputs

    def test_create_manual_annotation_formats_node_output(self):
        """Test create_manual_annotation_formats_node output."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "create_manual_annotation_formats_node"][0]
        
        assert node.outputs == ["manual_annotations@PartitionedDataset"]

    def test_plot_observations_summary_node_inputs(self):
        """Test plot_observations_summary_node inputs."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "plot_observations_summary_node"][0]
        
        expected_inputs = ["observations@pamDP", "media@pamDP"]
        
        assert list(node.inputs) == expected_inputs

    def test_plot_observations_summary_node_output(self):
        """Test plot_observations_summary_node output."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "plot_observations_summary_node"][0]
        
        assert node.outputs == ["observations_summary@matplotlib"]

    def test_plot_observations_per_species_node_inputs(self):
        """Test plot_observations_per_species_node inputs."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "plot_observations_per_species_node"][0]
        
        expected_inputs = ["observations@pamDP"]
        
        assert list(node.inputs) == expected_inputs

    def test_plot_observations_per_species_node_output(self):
        """Test plot_observations_per_species_node output."""
        pipeline = create_pipeline()
        node = [n for n in pipeline.nodes if n.name == "plot_observations_per_species_node"][0]
        
        assert node.outputs == ["observations_per_species@matplotlib"]

    def test_data_flow_species_detection_to_filter(self):
        """Test data flows from species_detection_node to filter_observations_node."""
        pipeline = create_pipeline()
        
        species_detection = [n for n in pipeline.nodes if n.name == "species_detection_node"][0]
        filter_obs = [n for n in pipeline.nodes if n.name == "filter_observations_node"][0]
        
        # Output of species_detection is input to filter
        assert species_detection.outputs[0] == "unfiltered_observations@pamDP"
        assert "unfiltered_observations@pamDP" in filter_obs.inputs

    def test_data_flow_filter_to_segments(self):
        """Test data flows from filter_observations_node to create_segments_node."""
        pipeline = create_pipeline()
        
        filter_obs = [n for n in pipeline.nodes if n.name == "filter_observations_node"][0]
        create_seg = [n for n in pipeline.nodes if n.name == "create_segments_node"][0]
        
        # Output of filter is input to create_segments
        assert filter_obs.outputs[0] == "observations@pamDP"
        assert "observations@pamDP" in create_seg.inputs

    def test_data_flow_segments_to_folder_and_manual_annotation(self):
        """Test data flows from create_segments_node to both folder and manual annotation nodes."""
        pipeline = create_pipeline()
        
        create_seg = [n for n in pipeline.nodes if n.name == "create_segments_node"][0]
        seg_folder = [n for n in pipeline.nodes if n.name == "create_segments_folder_node"][0]
        manual_anno = [n for n in pipeline.nodes if n.name == "create_manual_annotation_formats_node"][0]
        
        # Output of create_segments is input to both nodes
        assert create_seg.outputs[0] == "segments@pandas"
        assert "segments@pandas" in seg_folder.inputs
        assert "segments@pandas" in manual_anno.inputs

    def test_plot_nodes_use_observations_output(self):
        """Test that plot nodes use observations from filter_observations_node."""
        pipeline = create_pipeline()
        
        filter_obs = [n for n in pipeline.nodes if n.name == "filter_observations_node"][0]
        plot_summary = [n for n in pipeline.nodes if n.name == "plot_observations_summary_node"][0]
        plot_species = [n for n in pipeline.nodes if n.name == "plot_observations_per_species_node"][0]
        
        # Output of filter is input to both plot nodes
        assert filter_obs.outputs[0] == "observations@pamDP"
        assert "observations@pamDP" in plot_summary.inputs
        assert "observations@pamDP" in plot_species.inputs

    def test_no_duplicate_node_names(self):
        """Test that no duplicate node names exist."""
        pipeline = create_pipeline()
        node_names = [node.name for node in pipeline.nodes]
        
        assert len(node_names) == len(set(node_names))

    def test_pipeline_accepts_kwargs(self):
        """Test that create_pipeline accepts **kwargs."""
        # Should not raise error
        pipeline = create_pipeline(test_param="value", another_param=123)
        assert isinstance(pipeline, Pipeline)

    def test_consistent_pipeline_creation(self):
        """Test that multiple calls create consistent pipelines."""
        pipeline1 = create_pipeline()
        pipeline2 = create_pipeline()
        
        names1 = [n.name for n in pipeline1.nodes]
        names2 = [n.name for n in pipeline2.nodes]
        
        assert names1 == names2