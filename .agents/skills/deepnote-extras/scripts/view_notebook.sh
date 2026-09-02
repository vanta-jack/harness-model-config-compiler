#!/usr/bin/env bash
# ==============================================================================
# view_notebook.sh — Fetch and inspect Deepnote notebook blocks via Public REST API v2
# ==============================================================================
set -euo pipefail

if [ -z "${DEEPNOTE_TOKEN:-}" ]; then
  echo "Error: DEEPNOTE_TOKEN environment variable is not set." >&2
  echo "Usage: view_notebook.sh <notebook-id> [--full | --raw | <jq-filter>]" >&2
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "Usage: $0 <notebook-id> [--full | --raw | <jq-filter>]" >&2
  echo "Examples:" >&2
  echo "  $0 685468c726594fac812490ee71f557d3" >&2
  echo "  $0 685468c726594fac812490ee71f557d3 --full" >&2
  echo "  $0 685468c726594fac812490ee71f557d3 '.notebook.inputs'" >&2
  exit 1
fi

NOTEBOOK_ID="$1"
MODE="${2:-summary}"

API_URL="https://api.deepnote.com/v2/notebooks/${NOTEBOOK_ID}"

RESPONSE=$(curl -s -f -H "Authorization: Bearer ${DEEPNOTE_TOKEN}" "${API_URL}")

case "${MODE}" in
  --full|--raw)
    echo "${RESPONSE}" | jq .
    ;;
  summary)
    echo "${RESPONSE}" | jq '.notebook.blocks[] | {id, type, content: (if .content then (.content | split("\n")[0]) else null end)}'
    ;;
  *)
    echo "${RESPONSE}" | jq "${MODE}"
    ;;
esac
