# Spec: Repository File Structure Layout

* **Status**: Accepted / Final
* **Date**: 2026-09-01
* **Category**: Specification
* **Aligned With**: [ADR 006: Repository Role & Execution Boundary](../../decisions/006-repository-role-and-execution-boundary.md) and [ADR 007: Notebook Format Hierarchy and Asynchronous Distribution](../../decisions/007-notebook-format-and-distribution-hierarchy.md)
* **Supersedes**: Dataset placement convention from ADR 003

---

## 1. Context

Following ADR 006 and ADR 007, this repository functions as a **shape-tracking scaffold** where authoring and execution occur in Deepnote Cloud. This specification defines the canonical top-level folder layout and operational boundaries of the repository.

---

## 2. Canonical Layout

```text
model-config-crafter/
├── deepnote/                        # Primary Source of Truth: .deepnote files
│   ├── *.deepnote                   # Native YAML notebooks (inspected/verified by agents)
│   └── snapshots/                   # CLI run outputs (gitignored)
├── notebooks/                       # Downstream export artifacts (.ipynb)
│   └── *.ipynb                      # Generated on-demand via deepnote convert
├── sample-datasets/                 # Tracked reference dataset samples
├── datasets/                        # Gitignored local scratchpad (NOT an architectural artifact)
├── docs/
│   ├── decisions/                   # Architectural Decision Records (ADRs)
│   ├── superpowers/
│   │   └── specs/                   # Implementation specifications (including this file)
│   └── postmortems/                 # Operational incident post-mortems
└── .agents/                         # Agent tooling, skills, and MCP configurations
```

---

## 3. Directory Contracts & Responsibilities

### A. `deepnote/` (Primary Source of Truth)
* **Format**: `.deepnote` (YAML).
* **Ingestion**: Pushed from Deepnote Cloud via its GitHub integration, or updated programmatically via Deepnote MCP.
* **Role**: The authoritative representation of the project's logic, pipeline DAGs, and UI widget schemas ([ADR 005](../../decisions/005-deepnote-input-widget-metadata-schema.md)). AI coding agents inspect and verify project state against files in this folder.

### B. `notebooks/` (On-Demand Export Target)
* **Format**: `.ipynb` (JSON).
* **Generation**: Generated on-demand using the Deepnote CLI:
  ```bash
  deepnote convert deepnote/<notebook>.deepnote -t ipynb -o notebooks/<notebook>.ipynb
  ```
* **Role**: Downstream distribution target for external environments (Google Colab, Kaggle, local JupyterLab).
* **Parity Policy**: Explicitly asynchronous. 100% real-time synchronization with `deepnote/` is not required or enforced.

### C. `sample-datasets/` (Tracked Reference Samples)
* **Role**: Contains small, anonymized, or illustrative dataset samples version-controlled in Git for documentation, schema testing, and reference examples.

### D. `datasets/` (Local Scratchpad)
* **Role**: Local temporary data store. Strictly gitignored. It is not an architectural artifact and carries no runtime dependency for Deepnote Cloud execution.

---

## 4. Key Architectural Principles

1. **Flat Project Structure**: As a single-tool repository ([ADR 002](../../decisions/002-deepnote-workspace-sync-boundaries.md)), notebooks sit directly under `deepnote/` and `notebooks/` without redundant project-level subfolder nesting.
2. **Encapsulation of Cloud Execution**: Notebook execution occurs in Deepnote Cloud. The local repository does not replicate cloud `/work` paths.
3. **Diff Hygiene**: Only `.deepnote` YAML files are tracked for day-to-day development, keeping Git commits concise and meaningful.
