# Hermes Agent Config Compiler Specification (`04a_compiler_hermes`)

> [!NOTE]
> **Amended by ADR 011**: Clarifies `providers.*` isolation, deliberate exclusion of upstream pricing/cost columns from YAML, and optional field taxonomy (OpenRouter routing, Azure auth, and reserving `extra_headers` strictly for 1% proxy edge cases).
>
> **Amended by ADR 012**: Enforces universal path standard to eliminate root directory clutter and stale cache shadowing.
>
> **Amended by ADR 013**: Establishes 3-tier ETL directory boundary: `datasets/` (Raw Kaggle corpus) $\to$ `intermediate/` (Curated subsets `intermediate/pinned-models.json`) $\to$ `outputs/` (Compiled manifests `outputs/hermes-providers.yaml`).

**Document Metadata**
* **Date**: 2026-09-01
* **Status**: Validated Design Specification (v1.2 — Comprehensive In-Notebook Guides)
* **Target Notebook**: `04a_compiler_hermes` (ID: `b7c9d8922eb44fa0a7c792c30d2f0b5a`)
* **Upstream Feeder**: `02_schema` (ID: `685468c726594fac812490ee71f557d3`) via `pinned-models.json`
* **Contract Reference**: `docs/contracts/hermes-config.yaml.example` (Lines 127–168)
* **Standard Interface**: `compiler_general_instructions` (ID: `bd23c2740d5b4827b2d7ba835ded8295`)

---

## 1. Executive Summary & Scope Boundary

The `04a_compiler_hermes` notebook is an interactive, human-in-the-loop (HITL) configuration compiler that transforms un-normalized model records from `02_schema` (`pinned-models.json`) into modular Hermes Agent configuration stanzas and companion `.env` credential manifests.

### Scope Invariants
1. **Isolated `providers.*` Focus**: The compiler focuses strictly on generating named provider stanzas under `providers.<provider_name>` and declaring required secret keys in `.env`. Global `model.*` configuration settings are left untouched to prevent overwriting user defaults.
2. **Single-Provider Ingestion Alignment**: Ingested datasets originate 1:1 from single-provider catalog snapshots (`01_ingestion`). Therefore, each `04a` compile run targets exactly one named provider stanza.
3. **Zero-Assumption Zero-Defaults**: Input widgets initialize blank (`""`). The compiler enforces explicit human intent and never silently fabricates field mappings.
4. **Pre-Flight Diagnostic Auditing**: Before rendering or exporting manifests, the engine executes a loud diagnostic audit categorizing missing dimensions into fail-fast critical errors, harness risk warnings, and contract notices.
5. **Unified Diff Dry-Run Engine**: The dry-run execution generates a full unified diff (`difflib.unified_diff`) against live target configuration files (`~/.hermes/config.yaml` and `.env`), displaying exact visual diffs and full merged file previews before deployment.
6. **Self-Documenting In-Notebook Guides**: Every section includes comprehensive markdown walkthroughs, field definitions, callouts, and concrete examples (e.g. `featherless`, `deepinfra`).

---

## 2. Pipeline Architecture & Data Flow

```
┌────────────────────────────────────────────────────────┐
│ 01_ingestion (Catalog Fetcher)                         │
│ • Ingests single provider /v1/models catalog           │
│ • Vaults: datasets/<provider>-models-YYYYMMDD-HHMM.json│
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 02_schema (Discovery & Curation Workbench)             │
│ • Profiles dot-paths without destructive normalization │
│ • Filters & pins model subset                          │
│ • Emits: pinned-models.json (Active Scratchpad)        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 04a_compiler_hermes (Hermes Provider Compiler)         │
│ • 1. Raw Dataset Table Display                         │
│ • 2. Zero-Default Field & Provider Mappings            │
│ • 3. Pre-Flight Diagnostic Audit Engine                │
│ • 4. Manifest Generation (providers.<name> & .env)     │
│ • 5. Dry-Run Full Config Unified Diff & Export Engine  │
└────────────────────────────────────────────────────────┘
```

---

## 3. Detailed In-Notebook Instructional Content

The notebook includes self-documenting markdown cells for each phase:

### Block 00: Architecture Overview & Credential Policy
```markdown
# 04a — Hermes Agent Config Compiler

An interactive compiler that transforms curated model datasets into modular Hermes Agent provider configurations (`providers.<name>`) and companion `.env` credential manifests.

### Hermes Architecture & Credential Model
* **Modular Provider Stanzas**: Hermes supports per-provider overrides under the `providers:` section in `~/.hermes/config.yaml` (or profile directories like `~/.hermes/profiles/<profile>/config.yaml`). This compiler leaves your global `model:` defaults intact and generates an isolated provider block.
* **Secret Key Decoupling**: Hermes does not hardcode API keys in `config.yaml`. Instead, each provider specifies `key_env: "<VAR_NAME>"`, pointing to a credential expected in `.env`.
* **Workflow**: 
  1. Inspect the raw pinned table from `02_schema`.
  2. Declare column mappings and provider endpoint parameters below.
  3. Review the Pre-Flight Diagnostic Audit for token limit or timeout warnings.
  4. Run the **Dry Run Import** to preview a unified diff against your live Hermes configuration before deploying.
```

### Block 01: Dataset Selection Guide
```markdown
## 1. Select Pinned Dataset

Specify the pinned dataset snapshot generated by `02_schema` (defaults to active scratchpad `pinned-models.json`).
```

### Block 04: Provider Configuration & Field Mappings Guide
```markdown
## 2. Provider Configuration & Field Mappings

Declare the target provider endpoint, credential variable name, and map the table column headers to Hermes model fields.

### Mapping Reference & Examples:
* **`hermes_provider_name`** *(Required)*: The provider key name under `providers:` (e.g. `featherless`, `deepinfra`, `openrouter`).
* **`hermes_base_url`** *(Required for custom endpoints)*: The OpenAI-compatible API base URL (e.g. `https://api.featherless.ai/v1` or `https://api.deepinfra.com/v1/openai`). Note: ensure the `/v1` suffix is included.
* **`hermes_key_env`** *(Required)*: The exact environment variable name for the API key in `.env` (e.g. `FEATHERLESS_API_KEY`, `DEEPINFRA_API_KEY`).
* **`map_model_id`** *(Required)*: The column header from the table above holding the model ID string (e.g. `id`).
* **`map_context_length`** *(Recommended)*: The column header for total context window.
* **`map_max_tokens`** *(Optional)*: The column header for maximum generation tokens.
* **`hermes_request_timeout`** *(Optional)*: Request timeout in seconds (blank = Hermes default 1800s).
* **`hermes_stale_timeout`** *(Optional)*: Non-streaming hung-call detector timeout in seconds (blank = Hermes default 90s).

> [!IMPORTANT]
> **Why Context Limits Matter in Hermes**: Hermes relies on `context_length` to calculate context compression triggers (`compression.threshold: 0.50`). If unmapped, Hermes attempts runtime auto-detection. For custom gateways or proxies that do not expose `/v1/models`, missing context lengths may cause premature compaction or hard context overflow errors.
```

### Block 14: Sorting DSL & Diagnostic Audit Guide
```markdown
## 3. Preview Snippet & Pre-Flight Diagnostics

Execute the compiler to run pre-flight diagnostics and generate syntax-highlighted previews of the Hermes YAML snippet and `.env` template.

### Sorting DSL Reference:
Format: `<column_name> <ASC|DESC> [, <column_name> <ASC|DESC> ...]`
* `id ASC` — Alphabetical order by model ID.
* `context_length DESC, id ASC` — Largest context window first, then by ID.
```

### Block 17: Quick Import & Deployment Guide
```markdown
## 4. Quick Import & Deployment

Deploy the compiled provider configuration to your Hermes installation.

* **Dry Run Import**: Compares your generated configuration against your live `~/.hermes/config.yaml` and `.env` files. Renders a git-style **unified color diff** showing exact line-by-line changes and a full merged file preview without modifying any files on disk.
* **Targeted Import**: Non-destructively merges the `providers.<name>` block into your live `config.yaml` and appends missing secret keys to `.env`.
```

---

## 4. Interactive Input Widget Specification

All widgets initialize to `""` (no hardcoded defaults).

| # | Variable Name | Widget Type | Widget Label | Requirement Tier | Description / Validation |
| :- | :--- | :--- | :--- | :--- | :--- |
| **02** | `input_pinned_file` | `input-text` | `Pinned Models Input File` | Optional | Path to JSON file (falls back to `pinned-models.json` if blank). |
| **05** | `hermes_provider_name` | `input-text` | `Hermes Provider Stanza Name (e.g. featherless)` | **FAIL-FAST REQUIRED** | Named key under `providers:` (e.g. `featherless`, `deepinfra`). |
| **06** | `hermes_base_url` | `input-text` | `Provider Base URL (e.g. https://api.featherless.ai/v1)` | **FAIL-FAST REQUIRED** | Full API endpoint URL. |
| **07** | `hermes_key_env` | `input-text` | `API Key Env Var Name (e.g. FEATHERLESS_API_KEY)` | **FAIL-FAST REQUIRED** | Environment variable name declared in `.env`. |
| **08** | `map_model_id` | `input-text` | `Model ID Column Header (from table above)` | **FAIL-FAST REQUIRED** | Column name in `pinned-models.json` holding the model ID string. |
| **09** | `map_context_length` | `input-text` | `Context Window Column Header (e.g. context_length)` | **AUDITED WARNING** | Column name for total context window. If unmapped, emits warning. |
| **10** | `map_max_tokens` | `input-text` | `Max Output Tokens Column Header (leave blank if none)` | **AUDITED WARNING** | Column name for max generation tokens. If unmapped, emits warning. |
| **11** | `hermes_request_timeout` | `input-text` | `Request Timeout Seconds (blank = default 1800s)` | Optional | Timeout kwarg for turn client. |
| **12** | `hermes_stale_timeout` | `input-text` | `Non-Stream Stale Timeout Seconds (blank = default 90s)` | **AUDITED NOTICE** | Hung-call detector timeout. |
| **13** | `hermes_extra_headers` | `input-textarea` | `Extra HTTP Headers JSON (e.g. {"User-Agent": "curl/8.7.1"})` | Optional | Custom proxy/WAF headers dict. |
| **15** | `models_sort_dsl` | `input-text` | `Sorting DSL Expression (e.g. context_length DESC, id ASC)` | Optional | DSL for ordering models. |
| **18** | `hermes_target_dir` | `input-text` | `Target Deployment Directory (default: ~/.hermes)` | **FAIL-FAST REQUIRED** | Path to Hermes profile (e.g. `~/.hermes` or `~/.hermes/profiles/dev`). |

---

## 5. Pre-Flight Diagnostic Audit Engine

Before generating the preview or writing artifacts, Block 16 executes comprehensive validation:

### Diagnostic Severity Tiers
1. **`[FAIL-FAST CRITICAL]` (Blocks Generation)**:
   * Missing `input_pinned_file` on disk.
   * `hermes_provider_name` is blank.
   * `hermes_base_url` is blank.
   * `hermes_key_env` is blank.
   * `map_model_id` is blank or not found in the DataFrame columns.
2. **`[HARNESS RISK WARNING]` (Loud Notice — Proceed with Caution)**:
   * `map_context_length` is unmapped or missing for any model.  
     *Notice*: *"Hermes context compression triggers depend on context_length. Misdetection may cause premature compression or hard 400 context overflows."*
   * `map_max_tokens` is unmapped.  
     *Notice*: *"Max output tokens unconstrained. Model generations may run unbounded or hit unmanaged output clipping."*
   * `hermes_base_url` lacks `/v1` suffix when pointing to OpenAI-wire endpoints.
3. **`[CONTRACT NOTICE]` (Informational Invariant Checks)**:
   * `hermes_stale_timeout` is blank.  
     *Notice*: *"Hermes default stale timeout (90s) will apply. Reasoning/thinking models may trip hung-call detection."*
   * `hermes_extra_headers` is blank on private/internal base URLs.

---

## 6. Complete 24-Block Notebook Blueprint

```
[00] MARKDOWN: Title & Hermes providers.* Architecture Overview (Full Guide)
[01] MARKDOWN: ## 1. Input Dataset Selection (Guide)
[02] INPUT-TEXT: input_pinned_file = ''
[03] CODE: Load dataset & display raw DataFrame with exact column headers
[04] MARKDOWN: ## 2. Provider Configuration & Field Mappings (Field Reference & Examples)
[05] INPUT-TEXT: hermes_provider_name = ''      [REQUIRED]
[06] INPUT-TEXT: hermes_base_url = ''           [REQUIRED]
[07] INPUT-TEXT: hermes_key_env = ''            [REQUIRED]
[08] INPUT-TEXT: map_model_id = ''              [REQUIRED]
[09] INPUT-TEXT: map_context_length = ''        [AUDITED WARNING]
[10] INPUT-TEXT: map_max_tokens = ''            [AUDITED WARNING]
[11] INPUT-TEXT: hermes_request_timeout = ''    [OPTIONAL]
[12] INPUT-TEXT: hermes_stale_timeout = ''      [AUDITED NOTICE]
[13] INPUT-TEXTAREA: hermes_extra_headers = ''  [OPTIONAL]
[14] MARKDOWN: ## 3. Preview Snippet & Pre-Flight Diagnostics (DSL Guide)
[15] INPUT-TEXT: models_sort_dsl = ''           [OPTIONAL]
[16] CODE: Diagnostic Audit Engine + YAML & .env Syntax Preview Renderer
[17] MARKDOWN: ## 4. Quick Import & Deployment (Dry-Run & Merge Guide)
[18] INPUT-TEXT: hermes_target_dir = ''         [REQUIRED]
[19] CODE: Local File Exporter (writes hermes-providers.yaml and hermes.env)
[20] BUTTON: "Dry Run Import"
[21] CODE: Dry Run Full Config Unified Diff & Validation Engine
[22] BUTTON: "Targeted Import"
[23] CODE: Targeted Deployment Script (applies merge to target config.yaml & .env)
```

---

## 7. Quality & Verification Gates

1. **Self-Documenting UX**: Every section provides explicit instructions, field definitions, and realistic examples (`featherless`, `deepinfra`) directly in the notebook.
2. **Schema Integrity**: Output YAML parses as valid YAML without trailing comma artifacts or type coercion bugs.
3. **Fail-Fast Safety**: Executing Block 16 with empty mandatory fields halts with actionable instructions rather than generating corrupt YAML.
4. **Non-Destructive Dry-Run**: The dry run script performs zero writes on disk and renders a complete, human-verifiable unified diff before any target file is modified.
5. **Traceability**: All output files write deterministic comments identifying source dataset snapshot and timestamp.
