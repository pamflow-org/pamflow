# Running the workflow

To run the entire workflow, use:

```bash
pamflow run
```

This is equivalent to `kedro run` — pamflow is built on top of Kedro, so both commands work interchangeably.

For better control and to understand each processing step, it is often useful to run individual pipelines:

```bash
pamflow run --pipeline <pipeline_name>
```

A pipeline consists of multiple **nodes**, where each node represents a single processing task (for example, validating metadata, generating spectrograms, or running species detection).

To execute a specific node:

```bash
pamflow run --nodes <node_name>
```

To see the available nodes and pipelines, consult the workflow visualization and pipeline documentation.

For a complete list of execution options, see the [Kedro command reference](https://docs.kedro.org/en/1.0.0/getting-started/commands_reference/#kedro-run)

