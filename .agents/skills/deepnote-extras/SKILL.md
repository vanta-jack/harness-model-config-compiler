---
name: deepnote-extras
description: Library of auditable, standalone CLI scripts for querying, inspecting, and dumping Deepnote workspaces, projects, and notebooks via the Public REST API v2
---

# Deepnote Extras Skill

## Overview
This skill provides a library of auditable, standalone CLI scripts for inspecting, querying, and exporting Deepnote resources via the Deepnote Public REST API v2. It provides structured, reproducible alternatives to ad-hoc curl commands and works alongside the Deepnote MCP tools.

---

> [!IMPORTANT]
> ### ⚠️ BRING YOUR OWN ENVIRONMENT VARIABLE (BYO-Env) CONTRACT
> All scripts in this library strictly follow the **Bring Your Own Environment Variable (BYO-Env)** model:
> * **Zero Local File Parsing**: Scripts **never** attempt to parse, search for, or source local configuration files like `.env`.
> * **Environment-Driven**: Scripts strictly expect required credentials (`DEEPNOTE_TOKEN`, and optionally `DEEPNOTE_PROJECT_ID`) to already be present in the active shell environment.
> * **Invocation Pattern**: Always ensure environment variables are exported before execution (e.g. `set -a && [ -f .env ] && source .env && set +a && ...`).

---

## Available Scripts

### 1. `dump_all_notebooks.py`
Consolidates all notebooks and block contents within a Deepnote Cloud project into a single structured Markdown megadump.

#### Usage
```bash
# Export using active DEEPNOTE_PROJECT_ID (defaults to /tmp/deepnote_project_megadump.md)
.agents/skills/deepnote-extras/scripts/dump_all_notebooks.py

# Export specific project to custom output location
.agents/skills/deepnote-extras/scripts/dump_all_notebooks.py \
  --project-id <PROJECT_UUID> \
  --output ./docs/cloud-notebooks-dump.md
```

---

### 2. `list_project_notebooks.sh`
Queries `https://api.deepnote.com/v2/projects/<project-id>` to list all notebook IDs, names, and metadata in a project.

#### Usage
```bash
# List all notebooks in a project
.agents/skills/deepnote-extras/scripts/list_project_notebooks.sh <project_id>

# Use active DEEPNOTE_PROJECT_ID environment variable
.agents/skills/deepnote-extras/scripts/list_project_notebooks.sh
```

---

### 3. `view_notebook.sh`
Queries `https://api.deepnote.com/v2/notebooks/<notebook-id>` to inspect individual notebook blocks, inputs, and code content.

#### Usage
```bash
# Summary view (prints block ID, type, and first line of content)
.agents/skills/deepnote-extras/scripts/view_notebook.sh <notebook_id>

# Full un-truncated JSON
.agents/skills/deepnote-extras/scripts/view_notebook.sh <notebook_id> --full

# Custom jq expression (e.g. view only inputs)
.agents/skills/deepnote-extras/scripts/view_notebook.sh <notebook_id> '.notebook.inputs'
```
