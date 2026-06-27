## Create a custom pipeline

Adding a new pipeline in pamflow is simple by using the Kedro CLI tools. Here is the straightforward, step-by-step process:

### 1. Generate the Pipeline

Open your terminal in the root of your Kedro project and run the following command:

```bash
kedro pipeline create [pipeline_name]

```

*(Replace `[pipeline_name]` with your desired name, e.g., `data_science` or `preprocessing`.)*

**What this does:**

* Creates a folder in `src/pamflow/pipelines/[pipeline_name]`.
* Generates template files: `nodes.py` (for your logic) and `pipeline.py` (for the structure).
* Creates a configuration file in `conf/base/[pipeline_name].yml`.

---

### 2. Define your Logic in `nodes.py`

Open `src/pamflow/pipelines/[pipeline_name]/nodes.py` and write your Python functions.

```python
def my_first_node(data):
    # Your transformation logic here
    return data.upper()

```

---

### 3. Connect the Nodes in `pipeline.py`

Open `src/pamflow/pipelines/[pipeline_name]/pipeline.py`. Use the `node()` function to map your Python functions to inputs and outputs defined in your **Data Catalog**.

```python
from kedro.pipeline import Pipeline, node
from .nodes import my_first_node

def create_pipeline(**kwargs):
    return Pipeline([
        node(
            func=my_first_node,
            inputs="raw_data_from_catalog",
            outputs="processed_data_output",
            name="transform_node",
        ),
    ])

```

---

### 4. Register the Pipeline
Open `src/pamflow/pipeline_registry.py` and update it in three places:

**1. Add the import at the top of the file:**
```python
from [your_project].pipelines.[pipeline_name] import pipeline as my_pipeline
```

**2. Instantiate the pipeline inside `register_pipelines()`:**
```python
def register_pipelines() -> Dict[str, Pipeline]:
    my_pipeline_instance = my_pipeline.create_pipeline()
    ...
```

**3. Add the pipeline to the return dictionary:**
```python
    return {
        "__default__": my_pipeline_instance,
        "[pipeline_name]": my_pipeline_instance,
    }
```


---

### 5. Verify and Run

To make sure Kedro sees your new pipeline, list them first:

```bash
kedro registry list

```

Then, run only your new pipeline to test it:

```bash
kedro run --pipeline [pipeline_name]
```

---

### Troubleshooting Tip: Check your Nodes

If the run fails, you can use the command we discussed earlier to see exactly how Kedro is interpreting your new pipeline's structure:

```bash
kedro pipeline describe [pipeline_name]

```
