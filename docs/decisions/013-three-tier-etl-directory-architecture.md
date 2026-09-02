# ADR 013: Three-Tier ETL Directory Taxonomy & Kaggle Boundary Isolation

* **Status**: Accepted
* **Date**: 2026-09-02
* **Category**: Diátaxis Explanation / Architectural Decision Record (ADR)
* **Domain**: Repository Layout, ETL Pipeline Boundaries, Kaggle Dataset Compatibility
* **Complements**: [ADR 009](./009-dataset-snapshot-timestamping-standard.md), [ADR 010](./010-curation-artifact-naming-and-pinned-derivation.md), [ADR 012](./012-dataset-path-uniformity-and-cart-lifecycle.md)

---

## 1. Context & Problem Statement

The repository serves two distinct functional missions:
1. **Public/Kaggle Dataset Collection**: Accumulating immutable, historical snapshots of model catalog metadata across AI inference providers.
2. **Harness Configuration Compilation**: Transforming curated model subsets into operational CLI/engine configuration files (Hermes Agent, Pi Coding Agent, LiteLLM).

Previously, transient curation scratchpads (`pinned-models.json`) and compiled operational manifests (`hermes-providers.yaml`, `hermes.env`) were mixed into `datasets/` or the root workspace directory. This caused:
* **Dataset Pollution**: Kaggle data packaging scripts (`kaggle datasets create -p datasets/`) ingested YAML configs, `.env` files, and transient pipeline caches alongside raw JSON catalogs.
* **Lack of ETL Separation**: Ingestion outputs (Bronze), Curation subsets (Silver), and Compiled configs (Gold) lacked clean architectural boundaries.

---

## 2. Decision: 3-Tier ETL Directory Taxonomy

We establish a strict, standard 3-tier directory boundary across the entire pipeline:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. datasets/ (Raw Ingestion / Kaggle Dataset Corpus)                        │
│    • Immutable provider snapshots: datasets/<provider>-models-YYYYMMDD.json │
│    • Ephemeral fallback: datasets/models-list.json                          │
│    • Ingested by: 01_ingestion                                              │
│    • Purity: Zero operational configs, zero .env files, zero YAML           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. intermediate/ (Curated Subsets & Pipeline Handoffs)                      │
│    • Active curation scratchpad: intermediate/pinned-models.json            │
│    • Vaulted curation snapshots: intermediate/<stem>-pinned.json            │
│    • Emitted by: 02_schema                                                  │
│    • Consumed by: 04a_compiler_hermes, 04b_compiler_pi, 04c_compiler_litellm│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. outputs/ (Compiled Deployable Configuration Manifests)                   │
│    • Hermes: outputs/hermes-providers.yaml, outputs/hermes.env              │
│    • Pi: outputs/pi-models.json                                             │
│    • LiteLLM: outputs/litellm-config.yaml                                   │
│    • Emitted by: 04x compilers                                              │
│    • Consumed by: External Agent CLI runtimes (~/.hermes, ~/.pi, etc.)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Directory Invariants & Lifecycle Rules

1. **`datasets/` Purity Invariant**:
   * Contains exclusively provider model catalog datasets.
   * Directly packagable to Kaggle without filtering.
2. **`intermediate/` Pipeline State**:
   * Holds inter-notebook handoff data (`pinned-models.json`).
   * Is git-versioned or transiently shared across Deepnote workspaces.
3. **`outputs/` Target Manifests**:
   * Dedicated home for all compiled target artifacts (`.yaml`, `.env`, `.json`).
   * Dry-run engines and local file exporters write here, never to root or `datasets/`.

---

## 4. Implementation Plan & Affected Artifacts

| Notebook / File | Stage | Target Update |
| :--- | :--- | :--- |
| **`01_ingestion`** | Cloud (`273d00ed74624d798ca8b70bc3239742`) | Vaulted snapshots and ephemeral fallback write strictly to `datasets/`. |
| **`02_schema`** | Cloud (`685468c726594fac812490ee71f557d3`) | Input reads from `datasets/`. Exports write to `intermediate/pinned-models.json` and `intermediate/<stem>-pinned.json`. |
| **`04a_compiler_hermes`** | Cloud (`b7c9d8922eb44fa0a7c792c30d2f0b5a`) | Input reads from `intermediate/pinned-models.json`. Exporter writes to `outputs/hermes-providers.yaml` and `outputs/hermes.env`. |
| **`04b_compiler_pi` & `04c`** | Cloud (Downstream) | Input reads from `intermediate/pinned-models.json`. Exports write to `outputs/`. |
| **`2026-09-01-hermes-compiler-design.md`** | Spec Header | Add ADR 013 callout. |

---

## 5. Consequences

* **Positive**: Kaggle dataset directory is 100% pure and uncluttered.
* **Positive**: Clean, industry-standard Bronze/Silver/Gold ETL pipeline separation.
* **Positive**: Zero risk of operational configs leaking into public data releases.
