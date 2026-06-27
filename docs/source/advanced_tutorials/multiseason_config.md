## Multi‐Season Configuration

Kedro supports multiple seasonal configurations through environments and a global output path variable.

### Directory Structure

```
conf/
├── base/
│   ├── catalog.yml       ← shared catalog with ${globals:output_dir} references
│   ├── parameters.yml    ← shared default parameters
│   └── globals.yml       ← default output path (single-season projects stop here)
├── dry_2023/
│   ├── parameters.yml
│   ├── catalog.yml
│   └── globals.yml       ← overrides output_dir for this season
└── wet_2024/
    ├── parameters.yml
    ├── catalog.yml
    └── globals.yml
```

### 1. Set the Default Output Path

For projects with a single season, define the output path in `conf/base/globals.yml`:

```yaml
# conf/base/globals.yml
output_dir: data/output
```

This is enough. No season-specific files are needed and all runs write to `data/output/`.

### 2. Override per Season

For multi-season projects, add a `globals.yml` to each season's folder:

```yaml
# conf/dry_2023/globals.yml
output_dir: data/output_dry_2023

# conf/wet_2024/globals.yml
output_dir: data/output_wet_2024
```

### 3. Reference the Output Path in the Catalog

Use `${globals:output_dir}` in `conf/base/catalog.yml` so all datasets resolve to the correct season's folder automatically:

```yaml
# conf/base/catalog.yml
some_output_dataset:
  type: pandas.CSVDataset
  filepath: ${globals:output_dir}/some_subfolder/results.csv

another_output:
  type: pandas.ParquetDataset
  filepath: ${globals:output_dir}/another_subfolder/data.parquet
```

### 4. Run using environment

Single season (uses `conf/base/globals.yml`):
```bash
kedro run
```

Specific season:
```bash
kedro run --env=dry_2023
kedro run --env=wet_2024
```

Kedro merges `conf/base/` with the selected environment, with the environment values taking precedence. Each season writes to its own output folder, making reruns safe without overwriting previous results.