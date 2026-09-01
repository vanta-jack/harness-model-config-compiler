# Post-Mortem 002: Agent Specification Overspecification & Legacy Naming Drift

* **Date**: 2026-09-01
* **Severity**: Medium — documentation bloat, specification overreach, naming confusion
* **Status**: Resolved (Updated repository-file-structure-layout.md)

---

## 1. Summary

During the drafting of the repository file structure layout specification (`docs/superpowers/specs/repository-file-structure-layout.md`), the previous agent committed two primary governance failures:
1. **Specification Bloat & Overreach**: Enshrining already-working, out-of-scope directories (`sample-datasets/`, `docs/`, `.agents/`) into the spec instead of focusing solely on the structural delta.
2. **Legacy Naming Drift & Lack of Verification**: Propagating the dead project name `model-config-crafter` rather than verifying against the canonical repository name (`harness-model-config-compiler`).

---

## 2. Root Cause Analysis

### A. Overspecification and Directory Bloat
The agent failed to apply standard scoping discipline (YAGNI). Rather than specifying only what was changing or actively governed by the architectural decision, the agent restated existing, untouched subsystems:
* Version-controlled reference datasets (`sample-datasets/`)
* Project documentation and decisions (`docs/`)
* Agent configurations and skills (`.agents/`)

This expanded the specification's footprint unnecessarily, conflating immutable background structure with active layout governance.

### B. Legacy Naming Drift
The agent reused stale terminology (`model-config-crafter`) from earlier uncommitted drafts without checking the active workspace root, repository metadata, or environment configurations, introducing cognitive drift into official repository documentation.

---

## 3. Corrective Actions

1. **Pruned Specification**: Rewrote `docs/superpowers/specs/repository-file-structure-layout.md` to strip out all untouched directories (`sample-datasets/`, `docs/`, `.agents/`) and focus purely on the dynamic sync boundary (`deepnote/` and `notebooks/`).
2. **Canonical Identity Alignment**: Restored canonical project naming (`harness-model-config-compiler`) across all structural documentation.

---

## 4. Directives for Future Agents

* **Specify Only the Delta**: Do not specify existing, untouched directories in layout specs. If a directory is not being altered or newly governed, leave it out of the specification.
* **Verify Repository Names**: Never assume project or repository names from memory or past conversation turns; verify against repository root directory names and configuration files before authoring specifications.
