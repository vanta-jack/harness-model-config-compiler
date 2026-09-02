# Agent Instructions

> [!WARNING] FAILURE TO FOLLOW THESE OPERATIONAL PROCEDURES IS GROUNDS FOR IMMEDIATE TERMINATION. AGENT MUST STRICTLY FOLLOW THIS REPOSITORY's GOVERNANCE AND CONSTRAINTS

## Workflow

### General

- Read the Deepnote skill and use Deepnote MCP to work with notebooks
- Interact with the cloud notebook directly via **Deepnote MCP tools** (`update_block`, `create_block`, `get_notebook`, `get_project`) using the resolved `DEEPNOTE_PROJECT_ID`.
- **Resolving Cloud Notebook IDs**: Deepnote MCP summarization omits child `notebookId` arrays. When an ID is unresolved, query Deepnote Public REST API v2 using the auditable helper script in `.agents/skills/deepnote-extras/`:
  ```bash
  set -a && [ -f .env ] && source .env && set +a && .agents/skills/deepnote-extras/scripts/list_project_notebooks.sh
  ```
- Files on disk use `kebab-case` (`models-list.json`, `pinned-models.json`); Python variables use `snake_case`.



## Notable Directories

- **docs**/: details architectural decisions and acts as a source of truth for the repo
- **deepnote-workspace/**: a 1:1 mirror of the deepnote workspace. Treat as a view-only may contain other files outside harness-model-config-compiler. This directory is never committed because it is a runtime directory
- **deepnote-workspace/Apps/harness-model-config-compiler/** or `CUSTOM_DEEPNOTE_WORKING_DIR`: check out this folder when referencing the shape of deepnote notebooks. 
- **notebooks/**: auto-generated notebooks from `.deepnote`. serves as static assets and does not always reflect real-time notebook status.
- **sample-datasets/**: examples of `.json` datasets strictly used as reference


## Important documentation reference

For detailed rationale and post-mortems, consult the decision records in `docs/*`.