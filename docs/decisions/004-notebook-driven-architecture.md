# ADR 004: Notebook-Driven Modularity & App Architecture

**Status:** Accepted
**Date:** 2026-08-31
**Category:** Diátaxis Explanation / Architectural Decision Record (ADR)
**Domain:** Workspace Architecture

---

## 1. Context and Problem Statement

The initial architecture (ADR 003) forced a standard Python SWE package layout (`src/`, `pyproject.toml`) onto the project. While this is standard for traditional software, it became an active anti-pattern for a Deepnote-centric "vibe-coding" workflow. 

When upstream LLM API provider schemas inevitably change, having extraction and compilation logic buried in hidden `.py` modules requires editing without visual feedback and constantly restarting the notebook kernel. This destroys the interactive feedback loop that makes Deepnote valuable.

## 2. Decision

We are adopting a **Notebook-Driven Architecture**. The `src/` directory and `pyproject.toml` have been deleted.

Instead of hidden Python modules, we are separating concerns into dedicated, numbered `.ipynb` workbenches. This provides isolated, visual playgrounds for trial-and-error (e.g., parsing volatile schemas) while keeping the execution DAG clear.

### Architecture Topology

**Sequential Core:**
* `01_ingestion.ipynb` — Backend ETL. Hits APIs, saves raw `datasets/`. Supports "Hybrid Execution": uses Deepnote UI inputs for manual runs, but falls back to environment variables for headless cron jobs.
* `02_schema.ipynb` — Profiles raw schemas. Discovers the "most complete" model signature by scanning for maximum object depth/width.
* `03_curation.ipynb` — Slices and filters datasets. Persists pinned models to a persistent `pinned-models.json` state file (rejecting in-memory state).

**Parallel Compilers:**
* `04a_compiler_hermes.ipynb`
* `04b_compiler_pi.ipynb`
* `04c_compiler_litellm.ipynb`

**Presentation Layer:**
* `app.ipynb` — (Un-numbered for resilience). The lightweight, published Deepnote App that strings together the stable outputs for mobile-first consumption.

## 3. Consequences

* **Positive:** Complete preservation of the interactive, visual feedback loop required for vibe-coding volatile API schemas.
* **Positive:** `app.ipynb` remains extremely lightweight and mobile-responsive (iPhone), as it is decoupled from heavy ETL processing.
* **Positive:** Clear pipeline execution order via numerical prefixes in the Deepnote sidebar.
* **Negative:** Harder to write traditional `pytest` unit tests for the core logic, which is an acceptable trade-off for iteration speed in this specific domain.
