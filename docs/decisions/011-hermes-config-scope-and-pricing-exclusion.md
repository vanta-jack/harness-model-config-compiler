# ADR 011: Hermes Config Scope Boundaries, Pricing Metadata Exclusion & Optional Field Taxonomy

* **Status**: Accepted
* **Date**: 2026-09-02
* **Category**: Diátaxis Explanation / Architectural Decision Record (ADR)
* **Domain**: Downstream Compiler (`04a_compiler_hermes`), Hermes Contract & Field Boundaries
* **Complements**: [ADR 010](./010-curation-artifact-naming-and-pinned-derivation.md)

---

## 1. Context & Problem Statement

During design and verification of the `04a_compiler_hermes` configuration compiler, architectural boundaries and field scopes were refined to address:
1. Scope boundary between modular `providers.*` stanzas vs global `model.*` defaults.
2. Treatment of upstream pricing/cost columns emitted by `02_schema`.
3. Clear taxonomy between standard first-class configuration options (e.g. OpenRouter routing, Azure auth) and arbitrary HTTP header shims (`extra_headers`).

---

## 2. Decisions & Architectural Rules

### 1. Isolation of `providers.*` Stanzas
* `04a_compiler_hermes` exclusively targets named provider stanzas under `providers.<provider_name>` and declares required secret keys in `.env`.
* Global default model selection (`model.default`, `model.provider`) is left untouched to prevent overwriting user defaults during profile imports.

### 2. Exclusion of Upstream Pricing Columns from YAML
* Upstream pricing/cost columns discovered in `02_schema` (regardless of dynamic header naming, e.g. `pricing.input`, `pricing.prompt`, `input_cost`) are deliberately excluded from `hermes-providers.yaml`.
* **Rationale**: The Hermes CLI configuration parser does not define a `pricing` schema under `providers.<name>.models.<id>`. Injecting unsupported keys generates schema validation warnings on CLI startup.
* Pricing metadata remains preserved in source dataset snapshots and `02_schema` curation tables. An in-notebook callout explains this omission to the user.

### 3. Optional Field Taxonomy & Shimming Elimination
To ensure users are never forced to shim standard CLI features into raw JSON/header fields, Hermes configuration fields are strictly categorized:

* **First-Class Provider & Model Fields (Native Compiler Widgets)**:
  * `base_url`, `key_env`
  * `request_timeout_seconds`, `stale_timeout_seconds`
  * `models.<id>.context_length`, `models.<id>.max_tokens`
* **First-Class Provider Routing & Caching Extensions (Dedicated Optional Inputs)**:
  * OpenRouter Routing: `provider_routing.sort`, `provider_routing.only`, `provider_routing.ignore`, `provider_routing.order`, `provider_routing.require_parameters`, `provider_routing.data_collection`
  * OpenRouter Edge Caching: `openrouter.response_cache`, `openrouter.response_cache_ttl`
  * Azure Keyless Auth: `auth_mode: "entra_id"`, `entra.scope`
* **`extra_headers` Boundary (Reserved Strictly for 1% Edge Cases)**:
  * The `hermes_extra_headers` textarea is reserved strictly for true transport/proxy edge cases: Cloudflare Access service tokens (`CF-Access-Client-Id`, `CF-Access-Client-Secret`), custom corporate WAF bypass `User-Agent` strings, and proprietary reverse proxy headers.

---

## 3. Consequences

* **Positive**: Clean separation of concerns with zero schema validation warnings on Hermes startup.
* **Positive**: Standard features have first-class homes rather than requiring manual JSON gymnastics in `extra_headers`.
* **Positive**: Full provenance and traceability preserved without hardcoding upstream column names.
