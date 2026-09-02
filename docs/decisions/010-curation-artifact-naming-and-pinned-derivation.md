# ADR 010: Curation Artifact Lifecycle & Deterministic Pinned Model Derivation

* **Status**: Accepted
* **Date**: 2026-09-01
* **Category**: Diátaxis Explanation / Architectural Decision Record (ADR)
* **Domain**: Model Curation, Artifact Lifecycle & Downstream Compiler Contract
* **Complements**: [ADR 009](./009-dataset-snapshot-timestamping-standard.md)

---

## 1. Context & Problem Statement

Stage 02 schema profiling and model curation produces a subset of chosen models (`pinned_cart`) destined for downstream compiler stages (`04a`, `04b`, etc.). 

Previously, there was no standardized specification for:
1. Distinguishing between ephemeral single-run curation outputs and permanent vaulted subsets.
2. Formulating a deterministic relationship between a raw input snapshot (`datasets/<source>.json`) and its curated output (`datasets/<source>-pinned.json`).
3. Ensuring downstream compilers could predictably consume the curated artifact without manual parameter juggling.

---

## 2. Decision: Dual Lifecycle for Curated Pinned Models

We establish a dual-mode artifact lifecycle for curated model subsets emitted by `02_schema`:

```text
[Source Dataset]                                  [Curated Artifact]
─────────────────────────────────────────────────────────────────────────────
Ephemeral: models-list.json              ──►      pinned-models.json
Vaulted:   datasets/<stem>.json          ──►      datasets/<stem>-pinned.json
```

### Architectural Rules:

1. **Deterministic Suffix Derivation (`-pinned.json`)**:
   * When `02_schema` processes a vaulted snapshot from `datasets/`, the resulting curated output derives its filename by appending `-pinned.json` directly to the source filename stem:
     $$\texttt{datasets/featherless-models-20260831-0000.json} \longrightarrow \texttt{datasets/featherless-models-20260831-0000-pinned.json}$$
   * This guarantees full lineage and traceability back to the exact source catalog snapshot.

2. **Ephemeral Scratchpad Contract (`pinned-models.json`)**:
   * When curating from `models-list.json` or running in opt-out mode, the active cart exports to `pinned-models.json` in the root workspace.
   * `pinned-models.json` is treated as a transient pipeline scratchpad that gets overwritten on subsequent curation runs.

3. **Compiler Ingestion Protocol**:
   * Downstream compilers (`04a_compiler_hermes`, `04b_compiler_pi`, etc.) default to consuming `pinned-models.json` for rapid iterative execution.
   * Compilers accept an optional `pinned_file` input to compile specific historical vaulted snapshots (`datasets/<stem>-pinned.json`).

---

## 3. Consequences

* **Positive**: 1-to-1 deterministic relationship between source catalog snapshots and their curated subsets.
* **Positive**: Downstream compilers require zero manual configuration during standard pipeline execution.
* **Positive**: Zero ambiguity regarding whether an artifact is an active scratchpad (`pinned-models.json`) or a permanent snapshot (`<stem>-pinned.json`).
