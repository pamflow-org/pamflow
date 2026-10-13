# Configuration

pamflow uses [Kedro's configuration system](https://docs.kedro.org/en/0.19.8/configuration/configuration_basics.html). Files in `conf/local/` override those in `conf/base/`.

## `conf/base/`: defaults

Shared defaults distributed with pamflow. Do not edit them for a particular project.

- `parameters/*.yml`: parameters, one file per pipeline.
- `catalog/*.yml`: datasets (inputs and outputs), one file per pipeline.
- `globals.yml`: shared values, such as `output_dir` (default `data/output`).

## `conf/local/`: your project

Edit these two files to point pamflow to your data:

- `parameters.yml`: `audio_root_directory`, `timezone` and any parameter you want to change.
- `catalog.yml`: path to the field deployments sheet and to the target species file.

Only include the entries you change. Do not commit your personal paths, and never store credentials in `conf/`.

## More

See the [documentation](https://pamflow.readthedocs.io/en/latest/documentation/overview.html) for details, including [multi-season setups](https://pamflow.readthedocs.io/en/latest/advanced_tutorials/multiseason_config.html).
