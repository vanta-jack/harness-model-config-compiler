#!/usr/bin/env bash
# ==============================================================================
# list_project_notebooks.sh — List all notebooks in a Deepnote project
# ==============================================================================
set -euo pipefail

if [ -z "${DEEPNOTE_TOKEN:-}" ]; then
  echo "Error: DEEPNOTE_TOKEN environment variable is not set." >&2
  echo "Usage: list_project_notebooks.sh <project-id>" >&2
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "Usage: $0 <project-id>" >&2
  exit 1
fi

PROJECT_ID="$1"
API_URL="https://api.deepnote.com/v2/projects/${PROJECT_ID}"

curl -s -f -H "Authorization: Bearer ${DEEPNOTE_TOKEN}" "${API_URL}" | jq '.project.notebooks[] | {id, name, isInit, lastRunAt}'
