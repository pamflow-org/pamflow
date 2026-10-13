# Running the workflow

To run the entire workflow, use:

```bash
pamflow run
```

This is equivalent to `kedro run` — pamflow is built on top of Kedro, so both commands work interchangeably. This documentation uses `pamflow run`.

The complete workflow runs, in this order of dependencies, `filter_media`, `data_preparation`, `graphical_soundscape`, `acoustic_indices`, `species_detection` and `quality_control`. Two pipelines are **not** part of it and must be run explicitly: `detection_validation`, which needs the manual annotations reviewed by an expert, and `export`.

For better control and to understand each processing step, it is often useful to run individual pipelines:

```bash
pamflow run --pipeline <pipeline_name>
```

The valid names for `--pipeline` are:

| Pipeline | What it does | In `pamflow run` |
|----------|--------------|:----------------:|
| `data_preparation` | Standardizes recordings and field metadata into the pamDP format. | ✅ |
| `quality_control` | Timeline, locations, survey effort, audio outliers and timelapses. | ✅ |
| `graphical_soundscape` | Graphical soundscapes. | ✅ |
| `acoustic_indices` | Acoustic indices per deployment. | ✅ |
| `species_detection` | Species detection with BirdNET, audio segments and annotation files. | ✅ |
| `detection_validation` | Per-species thresholds from reviewed annotations. | |
| `export` | Converts the pamDP outputs to the GBIF (camtrapDP) format. | |
| `pamflow` | The complete workflow (same as the default). | ✅ |

`graphical_soundscape`, `acoustic_indices` and `species_detection` include the `filter_media` step, so they can be run on their own once `data_preparation` has been run. See the [pipeline details](pipeline_details.md) for the inputs, outputs and parameters of each one.

To work on a subset of the deployments, list them in `deployments_filter`, see [Filter media](pipeline_details.md#7-filter-media).

A pipeline consists of multiple **nodes**, where each node represents a single processing task (for example, validating metadata, generating spectrograms, or running species detection).

To execute a specific node:

```bash
pamflow run --nodes <node_name>
```

To list the available pipelines and see the nodes of a pipeline, use the Kedro registry (no additional installation needed):

```bash
kedro registry list
kedro registry describe <pipeline_name>
```

For example, `kedro registry describe species_detection` prints the node names of that pipeline. The pipeline documentation lists the inputs, outputs and parameters of each node.

For a complete list of execution options, see the [Kedro command reference](https://docs.kedro.org/en/0.19.8/development/commands_reference.html#run-the-project)

