# Using a Custom BirdNET-Trained Classifier

**pamflow**  supports the use of custom classifiers trained with BirdNET-Analyzer. This allows users to run species detection using their own `.tflite` model and associated labels file instead of the default BirdNET global classifier, expanding species detection's scope to different  taxa .

## Prerequisites

Before using a custom classifier, ensure you have:

* A BirdNET-trained `.tflite` classifier model.
* A corresponding labels file (`.txt`).
* A pamflow installation that includes support for custom BirdNET classifiers.

---

## 1. Prepare the Model Files

Place your classifier model and labels file in a location accessible to pamflow.

Example:

```text
data/
└── 
    input/
    └── custom_classifier/
        ├── frogs.tflite
        └── frogs_labels.txt
```

---

## 2. Configure the Classifier Parameters

Open your species detection parameters file and specify the paths to the model and labels.

```yaml
species_detection_parameters:
  n_jobs: 8

  classifier_model_path: data/input/custom_classifier/frogs.tflite
  classifier_labels_path: data/input/custom_classifier/frogs_labels.txt
```

If these values are not present at `species_detection_parameters` **pamflow** uses the BirdNet model as default

```yaml
species_detection_parameters:
  n_jobs: 8

  classifier_model_path: null
  classifier_labels_path: null
```

---

## 3. Label Format Requirements

The labels file must follow the format expected by BirdNET-Lib.

Each line must contain:

```text
scientific name_common name
```

Examples:

```text
Boana cinerascens_Demerara Falls tree frog
Boana pugnax_Chirique-Flusse tree frog
```

### Important

The separator between the scientific name and common name **must be a single underscore (`_`)**.

Correct:

```text
Boana cinerascens_Demerara Falls tree frog
```

Incorrect:

```text
Boana_cinerascens
Boana_cinerascens_Demerara_Falls_tree_frog
Boana cinerascens
Demerara Falls tree frog
```

The underlying BirdNET library expects labels in this format and may fail or produce incorrect species names if a different convention is used.

---

## 4. Geographic Filtering Behavior

When using the default BirdNET classifier, pamflow uses deployment latitude and longitude to generate a location-specific species list.

When a custom classifier is supplied:

```yaml
classifier_model_path: data/custom_classifier/frogs.tflite
classifier_labels_path: data/custom_classifier/frogs_labels.txt
```

location-based filtering is automatically disabled.

This is the expected behavior because custom classifiers are assumed to have been trained for a specific set of classes determined by the user.

---

## 5. Running Species Detection

Once the configuration has been updated, run the pipeline as usual:

```bash
pamflow run --pipeline species_detection
```

No additional commands are required.

pamflow will automatically:

1. Load the custom classifier.
2. Load the custom labels file.
3. Run inference using the custom model.
4. Export detections following the standard pamflow observations schema.

---

## Troubleshooting

### Invalid label format

If pamflow reports an error related to label formatting, verify that every label follows:

```text
scientific name_common name
```

and that exactly one underscore separates the two fields.

### Model and labels mismatch

If predictions appear incorrect or classes are missing, verify that:

* The labels file corresponds to the exact classifier used during training.
* The order of labels in the file matches the output order of the classifier.
* The number of labels matches the number of output classes in the model.

### No detections produced

Check that:

* The classifier was trained for the target taxa.
* The confidence threshold is not set too high.
* The audio format is supported and can be processed by BirdNET.


