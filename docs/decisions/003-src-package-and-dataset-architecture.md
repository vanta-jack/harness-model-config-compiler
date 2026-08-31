# ADR 003: Core Python Package Layout, Modular Compilers, and Dataset Vault Taxonomy

* **Status**: Superseded by ADR 004 (Notebook-Driven Architecture)
* **Date**: 2026-08-30
* **Category**: Diátaxis Explanation / Architectural Decision Record (ADR)
* **Domain**: Codebase Architecture & Data Engineering

---

## 1. Context & Problem Statement

Managing 15+ LLM providers and compiling configuration manifests across multiple agentic coding harnesses (Hermes Agent, Pi Coding Agent, LiteLLM) requires handling 20k+ model entries per catalog.

Cramming ingestion, schema normalization, regex searching, and configuration emission into raw notebook cells in `app.ipynb` leads to monolithic anti-patterns, untestable business logic, and browser DOM performance degradation.

---

## 2. Decision: The Standardized `src` Layout & Dataset Vault

We adopt a modular software architecture separating core logic from visual presentation:

```text
model-config-crafter/
├── pyproject.toml          # PEP 621 package metadata & dependencies
├── datasets/               # <provider>-models-<MMDDYY>.json snapshots
├── src/
│   └── model_config_compiler/
│       └── compilers/      # Target harness compiler modules
└── deepnote/               # Deepnote notebook UI layers
```

### Key Architectural Principles:

1. **Standardized Packaging (PEP 621)**:
   * Package distribution name: `model-config-compiler` (kebab-case).
   * Package import name: `model_config_compiler` (snake_case).
   * Declares core dependencies (`requests`, `pandas`, `pyyaml`, `python-dotenv`) in `pyproject.toml`.
2. **Dataset Naming Standard**:
   * All dataset snapshots must follow `<provider>-models-<MMDDYY>.json` (e.g. `featherless-models-083126.json`).
3. **Decoupled Business Logic**:
   * Reusable algorithms (schema discrepancy detectors, regex search, harness compilers) are implemented as pure Python modules under `src/model_config_compiler/`.
   * Notebooks (`app.ipynb`) remain thin declarative visual layers that import from `model_config_compiler`.

---

## 3. Consequences

* **Positive**: Business logic is 100% unit-testable via `pytest` without launching a Jupyter kernel.
* **Positive**: Fast vectorized data processing on 20k+ rows with sub-25ms UI response times.
* **Positive**: Adding a new provider adapter or downstream agent harness is modular and isolated.
* **Positive**: Datasets are cleanly structured for export to external analytics platforms (e.g., Kaggle).
