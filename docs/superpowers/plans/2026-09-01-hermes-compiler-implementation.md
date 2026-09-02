# Hermes Agent Config Compiler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the 24-block `04a_compiler_hermes` Deepnote cloud notebook (`b7c9d8922eb44fa0a7c792c30d2f0b5a`) to compile un-normalized `pinned-models.json` into modular Hermes `providers.<name>` YAML stanzas and companion `.env` files with a full unified diff dry-run engine.

**Architecture:** A human-in-the-loop (HITL) interactive notebook architecture featuring zero-default input widgets, a pre-flight diagnostic audit engine that loudly flags missing token limits and hung-call timeouts, a structured YAML/`.env` serializer, and a non-destructive `difflib.unified_diff` dry-run validator against live `~/.hermes/config.yaml`.

**Tech Stack:** Python 3.10+, Deepnote Public REST API v2 / Deepnote MCP (`create_block`, `update_block`, `delete_block`), PyYAML, `difflib`, `pandas`, `pytest`.

**Spec:** [`docs/superpowers/specs/2026-09-01-hermes-compiler-design.md`](file:///workspaces/harness-model-config-compiler/docs/superpowers/specs/2026-09-01-hermes-compiler-design.md)

## Global Constraints
* **Isolated `providers.*` Scope**: Only generate `providers.<provider_name>` stanzas; do NOT modify top-level `model.*` configuration.
* **Single-Provider Invariant**: Exactly one named provider per compilation run.
* **Zero Synthetic Defaults**: Input widgets initialize to `""`. Mandatory fields fail fast; optional fields are omitted from YAML when left empty.
* **Non-Destructive Dry-Run**: Dry-run must perform zero filesystem writes and output a full unified color diff.
* **Pure Standard Library Core**: Core compilation, sorting DSL, diagnostic engine, and diffing must use standard library (`difflib`, `json`, `pathlib`, `re`, `shutil`) + `pandas`/`pyyaml`.

---

### Task 1: Hermes Compiler Core Engine & Unit Tests

**Files:**
* Create: `src/compilers/hermes_engine.py`
* Create: `tests/test_hermes_engine.py`

**Interfaces:**
* Produces:
  * `parse_sort_dsl(df: pd.DataFrame, dsl: str) -> pd.DataFrame`
  * `run_preflight_audit(df: pd.DataFrame, config: dict) -> list[dict]`
  * `compile_hermes_yaml(df: pd.DataFrame, config: dict) -> str`
  * `compile_hermes_env(config: dict) -> str`
  * `generate_dry_run_diff(target_dir: str, new_yaml_str: str, key_env: str) -> dict`

- [ ] **Step 1: Write failing unit tests for sorting DSL and pre-flight audit**

```python
# tests/test_hermes_engine.py
import pytest
import pandas as pd
from src.compilers.hermes_engine import parse_sort_dsl, run_preflight_audit, compile_hermes_yaml, generate_dry_run_diff

def test_parse_sort_dsl():
    df = pd.DataFrame([
        {"id": "b", "context_length": 32000},
        {"id": "a", "context_length": 128000},
    ])
    sorted_df = parse_sort_dsl(df, "context_length DESC, id ASC")
    assert sorted_df.iloc[0]["id"] == "a"
    assert sorted_df.iloc[1]["id"] == "b"

def test_preflight_audit_flags_missing_mandatory_and_warnings():
    df = pd.DataFrame([{"id": "m1"}])
    config = {
        "hermes_provider_name": "",
        "hermes_base_url": "",
        "hermes_key_env": "KEY",
        "map_model_id": "id",
        "map_context_length": "",
        "map_max_tokens": "",
        "hermes_stale_timeout": "",
    }
    diagnostics = run_preflight_audit(df, config)
    crit = [d for d in diagnostics if d["level"] == "CRITICAL"]
    warn = [d for d in diagnostics if d["level"] == "WARNING"]
    notice = [d for d in diagnostics if d["level"] == "NOTICE"]
    
    assert any("hermes_provider_name" in d["message"] for d in crit)
    assert any("context_length" in d["message"] for d in warn)
    assert any("stale_timeout" in d["message"] for d in notice)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_hermes_engine.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'src.compilers.hermes_engine'`

- [ ] **Step 3: Implement `src/compilers/hermes_engine.py`**

```python
# src/compilers/hermes_engine.py
import difflib
import json
import re
from pathlib import Path
import pandas as pd
import yaml

def parse_sort_dsl(df: pd.DataFrame, dsl: str) -> pd.DataFrame:
    if not dsl or not dsl.strip():
        return df
    sort_cols = []
    ascending_flags = []
    for part in dsl.split(","):
        tokens = part.strip().split()
        if not tokens:
            continue
        col = tokens[0]
        direction = tokens[1].upper() if len(tokens) > 1 else "ASC"
        if col in df.columns:
            sort_cols.append(col)
            ascending_flags.append(direction != "DESC")
    if sort_cols:
        return df.sort_values(by=sort_cols, ascending=ascending_flags).reset_index(drop=True)
    return df

def run_preflight_audit(df: pd.DataFrame, cfg: dict) -> list[dict]:
    diagnostics = []
    # 1. Critical
    if not cfg.get("hermes_provider_name", "").strip():
        diagnostics.append({"level": "CRITICAL", "field": "hermes_provider_name", "message": "Provider Name is required."})
    if not cfg.get("hermes_base_url", "").strip():
        diagnostics.append({"level": "CRITICAL", "field": "hermes_base_url", "message": "Provider Base URL is required."})
    if not cfg.get("hermes_key_env", "").strip():
        diagnostics.append({"level": "CRITICAL", "field": "hermes_key_env", "message": "API Key Env Var Name is required."})
    m_id_col = cfg.get("map_model_id", "").strip()
    if not m_id_col:
        diagnostics.append({"level": "CRITICAL", "field": "map_model_id", "message": "Model ID Column Header is required."})
    elif m_id_col not in df.columns:
        diagnostics.append({"level": "CRITICAL", "field": "map_model_id", "message": f"Model ID Column '{m_id_col}' not found in dataset."})

    # 2. Warnings
    ctx_col = cfg.get("map_context_length", "").strip()
    if not ctx_col or ctx_col not in df.columns:
        diagnostics.append({"level": "WARNING", "field": "map_context_length", "message": "Context Length unmapped. Hermes compaction threshold calculation will rely on auto-detection or fail."})
    max_tok_col = cfg.get("map_max_tokens", "").strip()
    if not max_tok_col or max_tok_col not in df.columns:
        diagnostics.append({"level": "WARNING", "field": "map_max_tokens", "message": "Max Output Tokens unmapped. Generations will use model native ceiling."})
    base_url = cfg.get("hermes_base_url", "").strip()
    if base_url and not base_url.endswith("/v1") and not base_url.endswith("/v1/openai"):
        diagnostics.append({"level": "WARNING", "field": "hermes_base_url", "message": f"Base URL '{base_url}' lacks standard '/v1' suffix."})

    # 3. Notices
    if not cfg.get("hermes_stale_timeout", "").strip():
        diagnostics.append({"level": "NOTICE", "field": "hermes_stale_timeout", "message": "Stale timeout unmapped. Hermes default 90s hung-call detector applies."})
    return diagnostics

def compile_hermes_yaml(df: pd.DataFrame, cfg: dict) -> str:
    prov_name = cfg["hermes_provider_name"].strip()
    prov_entry = {
        "base_url": cfg["hermes_base_url"].strip(),
        "key_env": cfg["hermes_key_env"].strip(),
    }
    if cfg.get("hermes_request_timeout", "").strip():
        prov_entry["request_timeout_seconds"] = int(cfg["hermes_request_timeout"].strip())
    if cfg.get("hermes_stale_timeout", "").strip():
        prov_entry["stale_timeout_seconds"] = int(cfg["hermes_stale_timeout"].strip())
    if cfg.get("hermes_extra_headers", "").strip():
        try:
            prov_entry["extra_headers"] = json.loads(cfg["hermes_extra_headers"])
        except Exception:
            pass

    m_id_col = cfg["map_model_id"].strip()
    ctx_col = cfg.get("map_context_length", "").strip()
    max_tok_col = cfg.get("map_max_tokens", "").strip()

    models_dict = {}
    for _, row in df.iterrows():
        mid = str(row[m_id_col])
        m_meta = {}
        if ctx_col and ctx_col in row and pd.notna(row[ctx_col]) and str(row[ctx_col]).strip():
            try:
                m_meta["context_length"] = int(float(str(row[ctx_col])))
            except ValueError:
                pass
        if max_tok_col and max_tok_col in row and pd.notna(row[max_tok_col]) and str(row[max_tok_col]).strip():
            try:
                m_meta["max_tokens"] = int(float(str(row[max_tok_col])))
            except ValueError:
                pass
        models_dict[mid] = m_meta

    prov_entry["models"] = models_dict
    payload = {"providers": {prov_name: prov_entry}}
    return yaml.dump(payload, sort_keys=False, indent=2)

def compile_hermes_env(cfg: dict) -> str:
    key_name = cfg["hermes_key_env"].strip()
    return f"# Required credentials for Hermes provider: {cfg['hermes_provider_name']}\n{key_name}=your_key_here\n"

def generate_dry_run_diff(target_dir_str: str, new_yaml_str: str, key_env: str) -> dict:
    target_dir = Path(target_dir_str).expanduser()
    config_file = target_dir / "config.yaml"
    env_file = target_dir / ".env"

    new_dict = yaml.safe_load(new_yaml_str)
    new_prov_key = list(new_dict.get("providers", {}).keys())[0]

    # Merging logic
    if config_file.exists():
        existing_yaml_text = config_file.read_text(encoding="utf-8")
        existing_dict = yaml.safe_load(existing_yaml_text) or {}
        if "providers" not in existing_dict or not isinstance(existing_dict["providers"], dict):
            existing_dict["providers"] = {}
        existing_dict["providers"][new_prov_key] = new_dict["providers"][new_prov_key]
        merged_yaml_text = yaml.dump(existing_dict, sort_keys=False, indent=2)
        diff_lines = list(difflib.unified_diff(
            existing_yaml_text.splitlines(keepends=True),
            merged_yaml_text.splitlines(keepends=True),
            fromfile=str(config_file),
            tofile=str(config_file)
        ))
    else:
        existing_yaml_text = ""
        merged_yaml_text = new_yaml_str
        diff_lines = list(difflib.unified_diff(
            [],
            merged_yaml_text.splitlines(keepends=True),
            fromfile="/dev/null",
            tofile=str(config_file)
        ))

    # Env diff
    env_status = "already_set"
    env_diff = ""
    if env_file.exists():
        env_content = env_file.read_text(encoding="utf-8")
        if not re.search(rf"^\s*{re.escape(key_env)}\s*=", env_content, re.MULTILINE):
            env_status = "needs_addition"
            env_diff = f"+ {key_env}=your_key_here"
    else:
        env_status = "new_file"
        env_diff = f"+ {key_env}=your_key_here"

    return {
        "target_dir": str(target_dir),
        "config_exists": config_file.exists(),
        "diff_text": "".join(diff_lines),
        "merged_full_yaml": merged_yaml_text,
        "env_status": env_status,
        "env_diff": env_diff
    }
```

- [ ] **Step 4: Run unit tests to verify they pass**

Run: `pytest tests/test_hermes_engine.py -v`  
Expected: PASS (100% test passing)

- [ ] **Step 5: Commit core engine**

```bash
git add src/compilers/hermes_engine.py tests/test_hermes_engine.py
git commit -m "feat(compiler): add Hermes compiler engine and unit tests"
```

---

### Task 2: Cloud Notebook Authoring — Sections 1 & 2 (Blocks 00–13)

**Files:**
* Modify: Cloud Notebook `04a_compiler_hermes` (`b7c9d8922eb44fa0a7c792c30d2f0b5a`) via Deepnote MCP

**Interfaces:**
* Deletes initial 3 placeholder blocks from `04a_compiler_hermes`.
* Inserts Blocks 00–13 (Markdown guides, table loader, input widgets for dataset & provider mappings).

- [ ] **Step 1: Inspect and clear placeholder blocks in cloud notebook `04a`**

Fetch block IDs in `04a` via Deepnote REST API / view script, delete placeholders via `delete_block`.

- [ ] **Step 2: Create Blocks 00–03 (Title, Dataset Guide, Widget, and Data Loader)**

Call `create_block` via Deepnote MCP:
* Block 00: `markdown` with full Title & Architecture Guide.
* Block 01: `markdown` `## 1. Input Dataset Selection`.
* Block 02: `input-text` `input_pinned_file = ''`.
* Block 03: `code` loading `pinned-models.json` into `pd.DataFrame` and calling `display(df)`.

- [ ] **Step 3: Create Blocks 04–13 (Provider Guide & Mapping Widgets)**

Call `create_block` via Deepnote MCP:
* Block 04: `markdown` `## 2. Provider Configuration & Field Mappings` with full field reference and context limit callouts.
* Blocks 05–13: `input-text` / `input-textarea` widgets initialized to `''`:
  * `hermes_provider_name = ''`
  * `hermes_base_url = ''`
  * `hermes_key_env = ''`
  * `map_model_id = ''`
  * `map_context_length = ''`
  * `map_max_tokens = ''`
  * `hermes_request_timeout = ''`
  * `hermes_stale_timeout = ''`
  * `hermes_extra_headers = ''`

- [ ] **Step 4: Verify Blocks 00–13 in cloud notebook**

Run `.agents/skills/deepnote-via-api/scripts/view_notebook.sh b7c9d8922eb44fa0a7c792c30d2f0b5a` to verify all 14 blocks are created in sequence.

---

### Task 3: Cloud Notebook Authoring — Section 3 (Blocks 14–16)

**Files:**
* Modify: Cloud Notebook `04a_compiler_hermes` (`b7c9d8922eb44fa0a7c792c30d2f0b5a`) via Deepnote MCP

**Interfaces:**
* Inserts Block 14 (Markdown: Sorting DSL & Pre-Flight Diagnostics Guide).
* Inserts Block 15 (Input-Text: `models_sort_dsl = ''`).
* Inserts Block 16 (Code: Pre-Flight Diagnostic Audit Engine & Syntax Preview Renderer).

- [ ] **Step 1: Create Block 14 (Markdown Guide for Section 3)**

Call `create_block` via Deepnote MCP with DSL reference and diagnostic level explanations.

- [ ] **Step 2: Create Block 15 (Input Widget for Sorting DSL)**

Call `create_block` with type `input-text` and content `models_sort_dsl = ''`.

- [ ] **Step 3: Create Block 16 (Code: Diagnostic Engine & Preview Renderer)**

Call `create_block` with type `code` containing the interactive execution code:
* Collects all global widget variables.
* Executes `run_preflight_audit(df, cfg)` and prints rich formatted alert panels (`[FAIL-FAST CRITICAL]`, `[HARNESS RISK WARNING]`, `[CONTRACT NOTICE]`).
* If critical errors exist, stops execution cleanly with `return` / message.
* Executes `parse_sort_dsl(df, dsl)`.
* Compiles `yaml_str = compile_hermes_yaml(sorted_df, cfg)` and `env_str = compile_hermes_env(cfg)`.
* Prints syntax-highlighted YAML and `.env` previews.

- [ ] **Step 4: Verify Blocks 14–16 in cloud notebook**

Run view script to confirm block placement and code formatting.

---

### Task 4: Cloud Notebook Authoring — Section 4 (Blocks 17–23)

**Files:**
* Modify: Cloud Notebook `04a_compiler_hermes` (`b7c9d8922eb44fa0a7c792c30d2f0b5a`) via Deepnote MCP

**Interfaces:**
* Inserts Block 17 (Markdown: Deployment & Dry-Run Guide).
* Inserts Block 18 (Input-Text: `hermes_target_dir = ''`).
* Inserts Block 19 (Code: Local File Exporter `hermes-providers.yaml` & `hermes.env`).
* Inserts Block 20 (Button: `Dry Run Import`).
* Inserts Block 21 (Code: Full Config Unified Diff & Dry Run Engine).
* Inserts Block 22 (Button: `Targeted Import`).
* Inserts Block 23 (Code: Targeted Deployment Script).

- [ ] **Step 1: Create Blocks 17–19 (Deployment Guide, Target Dir Widget, Local Exporter)**

Call `create_block` via Deepnote MCP:
* Block 17: Markdown guide explaining non-destructive dry-run vs targeted import.
* Block 18: `input-text` `hermes_target_dir = ''`.
* Block 19: `code` writing `hermes-providers.yaml` and `hermes.env` locally for manual review/download and printing bash copy command.

- [ ] **Step 2: Create Blocks 20–21 (Dry Run Button & Unified Diff Engine)**

Call `create_block` via Deepnote MCP:
* Block 20: `button` labeled `"Dry Run Import"`.
* Block 21: `code` executing `generate_dry_run_diff(hermes_target_dir, yaml_str, key_env)` and rendering:
  * Unified color diff against `~/.hermes/config.yaml`.
  * `.env` status & additions.
  * Full resulting merged YAML view.

- [ ] **Step 3: Create Blocks 22–23 (Targeted Import Button & Execution Script)**

Call `create_block` via Deepnote MCP:
* Block 22: `button` labeled `"Targeted Import"`.
* Block 23: `code` performing non-destructive file merge to `hermes_target_dir/config.yaml` and appending secret key placeholder to `hermes_target_dir/.env`.

- [ ] **Step 4: Verify full 24-block sequence in cloud notebook**

Run view script to confirm all 24 blocks are present in sequential order.

---

### Task 5: End-to-End Verification

**Files:**
* Test: `tests/test_e2e_compiler.py`

**Interfaces:**
* Validates end-to-end integration with sample dataset snapshot `datasets/featherless-models-20260831-0000.json`.

- [ ] **Step 1: Write failing E2E test**

```python
# tests/test_e2e_compiler.py
import pytest
import json
import pandas as pd
from pathlib import Path
from src.compilers.hermes_engine import compile_hermes_yaml, compile_hermes_env, generate_dry_run_diff

def test_e2e_hermes_compilation(tmp_path):
    # Mock pinned dataset
    mock_pinned = [
        {"id": "meta-llama/llama-3.3-70b-instruct", "context_length": 131072, "max_tokens": 8192},
        {"id": "qwen/qwen-2.5-coder-32b-instruct", "context_length": 32768, "max_tokens": 8192}
    ]
    df = pd.DataFrame(mock_pinned)
    cfg = {
        "hermes_provider_name": "featherless",
        "hermes_base_url": "https://api.featherless.ai/v1",
        "hermes_key_env": "FEATHERLESS_API_KEY",
        "map_model_id": "id",
        "map_context_length": "context_length",
        "map_max_tokens": "max_tokens",
        "hermes_request_timeout": "120",
        "hermes_stale_timeout": "90",
        "hermes_extra_headers": ""
    }
    
    yaml_out = compile_hermes_yaml(df, cfg)
    env_out = compile_hermes_env(cfg)
    
    assert "providers:" in yaml_out
    assert "featherless:" in yaml_out
    assert "meta-llama/llama-3.3-70b-instruct:" in yaml_out
    assert "FEATHERLESS_API_KEY=your_key_here" in env_out
    
    # Dry run diff test
    diff_res = generate_dry_run_diff(str(tmp_path), yaml_out, "FEATHERLESS_API_KEY")
    assert diff_res["config_exists"] is False
    assert "+++ " in diff_res["diff_text"]
    assert "featherless:" in diff_res["merged_full_yaml"]
```

- [ ] **Step 2: Run E2E test to verify it passes**

Run: `pytest tests/test_e2e_compiler.py -v`  
Expected: PASS

- [ ] **Step 3: Commit and verify clean workspace**

```bash
git add tests/test_e2e_compiler.py docs/superpowers/plans/2026-09-01-hermes-compiler-implementation.md
git commit -m "feat(compiler): add E2E verification tests and complete implementation plan"
```
