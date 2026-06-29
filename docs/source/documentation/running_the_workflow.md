# Running the workflow

To run the entire workflow, you can use the following command

```bash
pamflow run
```

This is equivalent to `kedro run` — pamflow is built on top of Kedro, so both commands work interchangeably.

For better control and to understand each step, it's highly recommended to run the pipelines individually, especially during your first execution.

```bash
pamflow run --pipeline <pipeline_name>
```

For a finner grained execution, run individual nodes whithin a pipeline.

```bash
pamflow run --nodes <nodes_names>
```

Check the full list of posibilities to run the workflow in the [kedro documentation web page](https://docs.kedro.org/en/1.0.0/getting-started/commands_reference/#kedro-run).

