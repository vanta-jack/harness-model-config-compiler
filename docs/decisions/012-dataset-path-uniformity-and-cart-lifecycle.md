# ADR 012: Dataset Path Uniformity, Stale Shadowing Elimination & Cart Lifecycle Policy

* **Status**: Accepted
* **Date**: 2026-09-02
* **Category**: Diátaxis Explanation / Architectural Decision Record (ADR)
* **Domain**: Repository Architecture, Artifact Path Standards, Deepnote Cart Lifecycle
* **Complements**: [ADR 009](./009-dataset-snapshot-timestamping-standard.md), [ADR 010](./010-curation-artifact-naming-and-pinned-derivation.md), [ADR 011](./011-hermes-config-scope-and-pricing-exclusion.md)

---

## 1. Context & Problem Statement

An architectural review of pipeline execution revealed two structural defects:

1. **Root Directory Pollution & Stale Shadowing**:
   * Previously, ephemeral scratchpads (`models-list.json`, `pinned-models.json`) were emitted directly into the working directory root (`/work/`), while permanent vaulted datasets were saved in `/work/datasets/`.
   * Downstream notebooks used loose multi-path search heuristics that checked `./<file>` before `datasets/<file>`. If an older scratchpad lingered at root, downstream compilers read the **stale root file** even after a fresh upstream run.
   * Search heuristics also contained obsolete legacy paths (e.g. `/workspaces/model-config-crafter/`).

2. **Cart Accumulation State in `02_schema`**:
   * The curation cart in `02_schema` was strictly additive. Changing filter rules and clicking "Pin Current Selection" repeatedly accumulated models with no mechanism to overwrite or reset without restarting the Python kernel.
   * Proposing multiple separate UI buttons (`[ Clear Selection ]`, `[ Overwrite Selection ]`, `[ Pin Selection ]`) introduces button bloat and UI race conditions.

---

## 2. Decision & Architectural Standards

### 1. Universal `datasets/` Home for All Model JSON Artifacts
All JSON datasets across every stage must reside strictly within `datasets/`:

```text
datasets/
├── <provider>-models-YYYYMMDD-HHMM.json  # Ingestion snapshot (01_ingestion)
├── models-list.json                     # Ephemeral ingestion fallback (01_ingestion)
├── pinned-models.json                   # Active curation scratchpad (02_schema)
└── <stem>-pinned.json                   # Vaulted curated snapshot (02_schema)
```

No JSON data artifacts may be written directly to the project root directory (`/work/`).

### 2. Standardized Default Widget Values
* **`02_schema`**: `dataset_file` widget defaults to `datasets/models-list.json` (or latest snapshot).
* **`04a_compiler_hermes` (and downstream `04b`, `04c`)**: `input_pinned_file` widget defaults to `datasets/pinned-models.json`.

### 3. Deterministic Path Resolution Protocol
Every notebook replaces ad-hoc multi-path lists with a deterministic resolver:

```python
def resolve_dataset_path(target_name: str, default_rel: str) -> Path:
    raw = (target_name or "").strip() or default_rel
    p = Path(raw)
    
    # 1. Direct path (if absolute or explicitly includes directory)
    if p.exists() and p.is_file():
        return p
        
    # 2. Check within datasets/
    in_datasets = Path("datasets") / p.name
    if in_datasets.exists() and in_datasets.is_file():
        return in_datasets
        
    # 3. Check within deepnote/datasets/ (cloud working directory fallback)
    in_dn_datasets = Path("deepnote/datasets") / p.name
    if in_dn_datasets.exists() and in_dn_datasets.is_file():
        return in_dn_datasets
        
    raise FileNotFoundError(f"[FAIL FAST] Could not locate dataset '{raw}'. Checked: [direct, datasets/, deepnote/datasets/]")
```

All references to obsolete repository paths (`/workspaces/model-config-crafter/`) are removed.

### 4. Cart Lifecycle & Overwrite Control in `02_schema`
To avoid button bloat, `02_schema` retains **one single action button** (`[ Pin Models ]`) and introduces a 1-line boolean toggle widget:

```python
accumulate_mode = False  # False = Overwrite cart (default), True = Append to existing cart
```

* When `accumulate_mode == False`: `pinned_cart` is initialized fresh from the current `filtered_df` (clean overwrite).
* When `accumulate_mode == True`: `pinned_cart` adds new models to the existing session cart.

---

## 3. Implementation Plan & Affected Artifacts

| Component | Target Location | Actions Required |
| :--- | :--- | :--- |
| **`01_ingestion`** | Cloud Notebook (`273d00ed74624d798ca8b70bc3239742`) | Update fallback export path from `Path("models-list.json")` to `Path("datasets/models-list.json")`. |
| **`02_schema`** | Cloud Notebook (`685468c726594fac812490ee71f557d3`) | 1. Add `accumulate_mode` checkbox widget.<br>2. Update Block 04 path resolver.<br>3. Update Block 16 export to `Path("datasets/pinned-models.json")` and implement `accumulate_mode` logic. |
| **`04a_compiler_hermes`** | Cloud Notebook (`b7c9d8922eb44fa0a7c792c30d2f0b5a`) | 1. Update Block 02 widget label and default to `datasets/pinned-models.json`.<br>2. Update Block 03 path resolver to use deterministic resolution. |
| **Downstream Compilers** | `04b_compiler_pi`, `04c_compiler_litellm` | Inherit default input path `datasets/pinned-models.json`. |
| **Spec Callout** | `2026-09-01-hermes-compiler-design.md` | Add ADR 012 notice to header. |

---

## 4. Consequences

* **Positive**: Eliminates root directory clutter and prevents stale cache shadowing bugs.
* **Positive**: Simple, deterministic path resolution with zero hardcoded legacy paths.
* **Positive**: Curation cart state is fully controllable via a single clean toggle without UI button bloat.
