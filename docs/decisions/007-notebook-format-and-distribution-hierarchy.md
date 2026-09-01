# ADR 007: Notebook Format Hierarchy and Asynchronous Distribution

* **Status**: Accepted
* **Date**: 2026-09-01
* **Category**: Diátaxis Explanation / Architectural Decision Record (ADR)
* **Domain**: Artifact Formats & Multi-Platform Distribution

---

## 1. Context & Problem Statement

Building on [ADR 006: Repository Role & Execution Boundary](./006-repository-role-and-execution-boundary.md), this repository functions as a shape-tracking scaffold where authoring and execution happen in Deepnote Cloud.

We needed to establish the storage format for notebook files in the repository. The two candidate formats present competing trade-offs:
* **`.deepnote` (YAML)**: Offers superior line-by-line Git diffs, separates execution snapshots from source, and preserves custom Deepnote UI widget metadata schemas ([ADR 005](./005-deepnote-input-widget-metadata-schema.md)). However, it is not natively executable by standard Jupyter runtimes without conversion.
* **`.ipynb` (JSON)**: Globally portable across external platforms (Kaggle, Google Colab, local JupyterLab), but produces noisy Git diffs, embeds output blobs, and risks stripping proprietary Deepnote widget metadata.

Attempting to keep both formats in 100% bidirectional real-time synchronization introduces severe maintenance overhead and sync drift.

---

## 2. Decision: Two-Tiered Format Hierarchy & Asynchronous Export

We adopt a two-tiered format hierarchy with an explicit rejection of continuous dual-format synchronization:

```text
[Deepnote Cloud Workspace] (Authoring & Execution via UI / MCP)
         │
         ▼ (Git Push / Export to Git)
[deepnote/*.deepnote] (Primary Source of Truth — inspection & verification target)
         │
         ▼ (On-demand `deepnote convert` CLI)
[notebooks/*.ipynb] (Downstream export artifacts for Colab, Kaggle, Local Jupyter)
```

### Architectural Principles:

1. **`deepnote/*.deepnote` is the Sole Source of Truth in Git**:
   * All notebook logic, pipeline DAG structures, and input widget metadata contracts ([ADR 005](./005-deepnote-input-widget-metadata-schema.md)) are authored in Deepnote Cloud and tracked in Git exclusively as native `.deepnote` files.
   * AI agents and maintainers inspect and verify project state using `deepnote/*.deepnote`.
   * Updates flow into this directory via Deepnote's GitHub integration (Git push) or direct Deepnote MCP block interactions.

2. **`notebooks/*.ipynb` is an On-Demand Downstream Distribution Target**:
   * The `notebooks/` directory holds standard `.ipynb` files intended solely for external portability (e.g., sharing with Kaggle, Google Colab, or running in local Jupyter kernels).
   * Files in `notebooks/` are generated strictly on-demand via the Deepnote CLI (`deepnote convert`).

3. **Rejection of Continuous Dual-Format Parity**:
   * We explicitly reject any requirement or automated burden to maintain 100% real-time parity between `deepnote/` and `notebooks/`.
   * Drift between `.deepnote` and `.ipynb` is accepted by design; `.ipynb` files are refreshed only when an export artifact is actively needed.

---

## 3. Consequences

* **Positive**: Git history remains clean, readable, and free of noisy JSON diffs and cell execution metadata.
* **Positive**: Input widget metadata contracts ([ADR 005](./005-deepnote-input-widget-metadata-schema.md)) cannot be corrupted by external Jupyter serializers.
* **Positive**: Eliminates CI maintenance overhead and mental fatigue associated with dual-format synchronization.
* **Negative**: Users running notebooks locally in standard Jupyter or Google Colab must run a manual conversion step (`deepnote convert`) if the `.ipynb` archive has not been refreshed recently.
