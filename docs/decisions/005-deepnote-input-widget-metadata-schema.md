# ADR 005: Deepnote Input Widget Metadata Schema & Render Contract

* **Status**: Accepted
* **Date**: 2026-08-31
* **Category**: Diátaxis Explanation / Architectural Decision Record (ADR)
* **Domain**: Deepnote Notebook UI & Block Metadata Contracts

---

## 1. Context & Incident Report

During the programmatic generation of `01_ingestion.ipynb` via the Deepnote MCP API (`create_block`), the parameter input blocks (`provider_name`, `api_endpoint`, `api_key`, `save_model_data`) failed to render in the Deepnote web UI, displaying as malformed/broken widget blocks.

---

## 2. Root Cause Diagnostics

Comparing the working input blocks in `app.ipynb` and Deepnote's internal schema (`schema.ts` / `blocks-input.md`) revealed three distinct metadata schema deficiencies in the initial MCP payload:

1. **Missing Controlled State Keys on `input-text`**:
   * Deepnote's React input widget components require both `deepnote_variable_value` and `deepnote_variable_default_value` in the `metadata` payload.
   * Passing only `deepnote_variable_name` and `deepnote_input_label` leaves the widget state undefined in the UI runtime, causing rendering failures.

2. **Incompatible Label Key on `input-checkbox`**:
   * For checkboxes, Deepnote requires `deepnote_input_checkbox_label` (instead of `deepnote_input_label`).
   * Checkbox widgets also mandate boolean values for `deepnote_variable_value: true` and `deepnote_variable_default_value: true`.

3. **API Contract Differences (`update_block` vs `create_block`)**:
   * The Deepnote MCP `update_block` tool only accepts `content` and `integrationId`, not `metadata`.
   * Correcting metadata on malformed blocks requires deleting the block and creating a new block with the full metadata dictionary.

---

## 3. Decision: Strict Input Widget Metadata Contract

All future programmatic creation of Deepnote input blocks must strictly adhere to the following metadata schemas:

### A. Text Inputs (`type: "input-text"`)
```json
{
  "deepnote_variable_name": "<var_name>",
  "deepnote_input_label": "<Display Label>",
  "deepnote_variable_value": "",
  "deepnote_variable_default_value": ""
}
```

### B. Checkbox Inputs (`type: "input-checkbox"`)
```json
{
  "deepnote_variable_name": "<var_name>",
  "deepnote_input_checkbox_label": "<Display Label>",
  "deepnote_variable_value": true,
  "deepnote_variable_default_value": true
}
```

---

## 4. Consequences

* **Positive**: All input widgets render reliably across Deepnote Cloud web and mobile UIs.
* **Positive**: Fully compliant with Deepnote's internal TypeScript definitions (`schema.ts`).
* **Operational Rule**: Never attempt to update block metadata via `update_block` — always delete and recreate with the full metadata object.
