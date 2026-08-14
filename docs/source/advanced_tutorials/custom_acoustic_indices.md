## Customize the acoustic indices to compute

**pamflow** computes a default set of acoustic indices, but you can enable or disable
individual indices, change their parameters, or add an entirely new index. Two files
are involved:

* **Configuration** — [`conf/base/parameters/acoustic_indices.yml`](https://github.com/) selects
  which indices run and with which parameters.
* **Implementation** — [`src/pamflow/pipelines/acoustic_indices/utils.py`](https://github.com/) contains
  the `AcousticIndices` class, where each index is implemented as one method.

See [Pipeline details — Acoustic indices](../documentation/pipeline_details.md) for the full
parameter reference table.

### 1. Enable or disable an index

Open `conf/base/parameters/acoustic_indices.yml`. Under `indices_settings`, each key is one
index:

```yaml
acoustic_indices:
  indices_settings: # List and paramters of acoustic indices
    ACI:
    ADI:
      fmin: 0
      fmax: 24000
      bin_step: 1000
      index: shannon
      dB_threshold: -40
    BI:
      flim: [2000, 11000]
    Hf:
    Ht:
    H:
    NDSI:
      flim_bioPh: [2000, 20000]
      flim_antroPh: [0, 2000]
    NP:
      mode: linear
      min_peak_val: 0
      min_freq_dist: 100
      slopes: null
      prominence: 1e-6
    RMS:
    SC:
      dB_threshold: -70
      flim_LF: [1000, 20000]
```

To skip an index, delete its key. For example, removing the `NP` block below stops the
Number of Peaks index from being computed — no other change is needed:

```yaml
    RMS:
    SC:
      dB_threshold: -70
      flim_LF: [1000, 20000]
```

To bring an index back, add its key again with the correct indentation.

### 2. Change an index's parameters

Edit the values under the index's key. For example, to compute the Acoustic Diversity Index
(ADI) up to 20 kHz instead of the default 24 kHz, change `fmax`:

```yaml
    ADI:
      fmin: 0
      fmax: 20000  # was 24000
      bin_step: 1000
      index: shannon
      dB_threshold: -40
```

```{tip}
`acoustic_indices.yml` is a plain YAML file, so it follows standard YAML rules:
- Indentation must use **spaces** consistently (2 spaces per nesting level) — never tabs.
- A key followed by nothing (e.g. `ACI:`) means "no parameters"; this is equivalent to `null`.
- Frequency ranges are written as inline lists: `[min, max]`.
- Lines starting with `#` are comments and are ignored.
```

### 3. Add a brand-new index (advanced)

The two steps above only toggle indices that pamflow already implements. Adding an index
that doesn't exist yet requires a small code change.

Each index is a method on the `AcousticIndices` class named `compute_<KEY>`, where `<KEY>`
matches the key used in `indices_settings`. When the pipeline runs, `compute_selected_indices()`
looks up one such method per key listed in the YAML and calls it. For example, the `ADI` key
in the config causes `compute_ADI` to be called:

```python
# src/pamflow/pipelines/acoustic_indices/utils.py
class AcousticIndices:
    ...
    def compute_ADI(self, params):
        """Compute Acoustic Diversity Index (ADI)."""
        return features.acoustic_diversity_index(self.Sxx, self.fn, **params)
```

To add a new index, add a matching method directly to the `AcousticIndices` class in
`src/pamflow/pipelines/acoustic_indices/utils.py`. For instance, `scikit-maad` (already
imported in that file as `features`) also provides the Acoustic Evenness Index, a natural
counterpart to ADI, which pamflow doesn't compute by default:

```python
def compute_AEI(self, params):
    """Compute Acoustic Evenness Index (AEI)."""
    return features.acoustic_eveness_index(self.Sxx, self.fn, **params)
```

Then enable it from the config, exactly as with any built-in index:

```yaml
    AEI:
      fmin: 0
      fmax: 20000
      bin_step: 500
      dB_threshold: -50
```

</content>
