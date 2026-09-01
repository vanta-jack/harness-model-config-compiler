# Spec: Repository File Structure Layout

* **Status**: Accepted
* **Date**: 2026-09-01
* **Category**: Specification

---

## 1. Canonical Layout Scope

This specification governs solely the dynamic synchronization and generated artifact directories:

```text
harness-model-config-compiler/
├── deepnote/                        # Workspace-wide sync viewing deck (mostly gitignored)
└── notebooks/                       # Generated/downstream notebooks (mostly gitignored)
```

---

## 2. Directory Roles

### A. deepnote/ (Workspace Viewing Deck)
* Populated via `deepnote sync` from the Deepnote Cloud workspace.
* Contains the entire synchronized workspace hierarchy, including projects outside `harness-model-config-compiler`.
* Zero hardcoded assumptions: expect anything or nothing in this directory.
* Used strictly as a local, read-only viewing deck for inspection.
* The repository does not depend on the internal structure of this folder. It is largely gitignored.

### B. notebooks/ (Generated Notebooks)
* Storage for notebooks generated or converted from Deepnote.
* Mostly gitignored.
