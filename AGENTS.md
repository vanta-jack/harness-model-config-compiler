# AGENTS.md — Operational Directives & Governance

Welcome, AI Agent. This repository hosts **`model-config-compiler`**, a modular configuration compiler and schema inspection workbench for agentic coding harnesses across 15+ LLM providers.

Before proposing or making any changes, you **MUST** strictly follow these repository governance directives and architectural constraints.

---

## 1. Repository Scope & Deepnote Mapping (Pattern 1)

* **Scope**: This Git repository represents **only this project** (`model-config-compiler`), not the user's entire Deepnote organization.
* **Deepnote Cloud Location**: Project `Agentic Harness Config Generator` located in the **`Apps`** folder of workspace.
* **Project ID Resolution**:
  1. **Primary**: Read the `DEEPNOTE_PROJECT_ID` environment variable (injected via Doppler or environment).
  2. **Fallback**: If unset, **halt and ask the user** for the target Project ID. Do not guess via name matching.
* **Sync Directive**: **NEVER run workspace-wide `deepnote sync` into the repository root.** Doing so will pollute this repository with external workspace projects.
* **Editing Directive**: Interact with the cloud notebook directly via **Deepnote MCP tools** (`update_block`, `create_block`, `get_notebook`, `get_project`) using the resolved `DEEPNOTE_PROJECT_ID`.

---

## 2. Secrets & MCP Configuration

* **Never hardcode secrets**: Do not commit API keys or auth tokens to Git.
* **Template Pattern**: The MCP config template (`.agents/mcp_config.json.template`) uses Doppler substitution syntax. The resolved local config (`.agents/mcp_config.json`) is gitignored.

---

## 3. Codebase Architecture (The `src` Layout)

* **`src/`**: Core Python package (`model_config_compiler`). All business logic, schema algorithms, and harness compilers live here. Installable via `pip install -e .`.
* **`datasets/`**: Provider model catalog snapshots following `<provider>-models-<MMDDYY>.json` naming.
* **`deepnote/`**: Deepnote notebook files. Notebooks are thin declarative UI layers that import from `model_config_compiler`.

* **No Monolithic Notebooks**: Business logic, schema normalization, and harness generators belong in `src/model_config_compiler/`. Notebooks should remain lightweight declarative visual layers.
* **Dataset Naming Standard**: All dataset snapshots must follow `<provider>-models-<MMDDYY>.json` (e.g. `featherless-models-083126.json`).

---

## 4. Architectural Decision Records (ADRs)

For detailed rationale and post-mortems, consult the decision records in `docs/decisions/`.
