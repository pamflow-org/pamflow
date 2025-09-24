# Documentation

## Running the entire pipeline

To run the entire workflow, you can use the following command

```bash
kedro run
```
However, for better control and to understand each step, it's highly recommended to run the pipelines individually, especially during your first execution.

## Running individual pipelines

### 1. Prepare data

This pipeline prepares your raw input data for analysis, ensuring it meets the required format and standards for subsequent steps.

```bash
kedro run --pipeline=prepare_data
```

### 2. Revise quality of deployments and recordings

After the data is prepared, this pipeline performs a series of checks to verify the quality of your deployments and recordings, identifying any issues before moving on to analysis.

```bash
kedro run --pipeline=quality_control
```

### 3. Detect species with AI

This pipeline utilizes AI models to automatically detect and identify species within your acoustic data.

```bash
kedro run --pipeline=species_detection
```

### 4. Compute Acoustic Indices

This step processes your audio files to calculate various acoustic indices. These indices provide a quantitative overview of the soundscape, useful for a wide range of analyses.

```bash
kedro run --pipeline=acoustic_indices
```

### 5. Generate Graphical Soundscapes

This step allows to compute a representation of the most prominent spectro-temporal dynamics over a 24-hour window per each deployment.

```bash
kedro run --pipeline=graphical_soundscape
```
