# ADR 006: Repository Role & Execution Boundary

* **Status**: Accepted
* **Date**: 2026-09-01
* **Category**: Diátaxis Explanation / Architectural Decision Record (ADR)
* **Domain**: Repository Governance & Execution Boundaries

---

## 1. Context & Problem Statement

As the project evolved from ADR 003 (src-based package) through ADR 004 (Notebook-Driven Architecture), the role of this Git repository became ambiguous. A recurring failure pattern emerged — both human maintainers and AI agents began treating the local repository structure as if it needed to mirror Deepnote Cloud's working directory (`/work`), leading to unnecessary architectural debates about runtime dataset paths, working directory co-location, and path traversal logic inside notebooks.

---

## 2. Decision: This Repository Is a Shape-Tracker

This repository is a **config-first, shape-tracking scaffold**. It is not a mirror of Deepnote Cloud's execution environment.

### What this repository IS responsible for:

* Tracking the **structure and content** of notebook files (`.deepnote`, `.ipynb`) as version-controlled artifacts.
* Storing **decisions** (`docs/decisions/`), **specs** (`docs/superpowers/specs/`), and **post-mortems** (`docs/postmortems/`).
* Holding **sample datasets** (`sample-datasets/`) as tracked reference examples.
* Providing a **gitignored local scratchpad** (`datasets/`) as a development convenience — not an architectural artifact.

### What this repository is NOT responsible for:

* Matching or mirroring Deepnote Cloud's `/work` directory structure.
* Satisfying notebook runtime path resolution (e.g., relative `./datasets/` paths executed in Deepnote Cloud).
* Replicating dataset files that Deepnote Cloud ingests, stores, or processes during execution.

### Execution Boundary

**All notebook execution happens in Deepnote Cloud.** This repository has no obligation to maintain file structures, dataset paths, or working directory conventions that serve Deepnote's runtime environment. Any decision about this repository's layout must be made on the basis of **repository ergonomics**, not Deepnote Cloud's execution mechanics.

---

## 3. Consequences

* **Positive**: Repository structure debates are scoped correctly. Questions about "where should datasets live so notebooks can find them" are irrelevant to this repository's design.
* **Positive**: Future agents and maintainers have a clear boundary. The repository answers to Git ergonomics and human readability, not to cloud execution paths.
* **Negative**: Engineers who are new to this project may instinctively attempt to mirror the execution environment locally. This ADR must be read first.
