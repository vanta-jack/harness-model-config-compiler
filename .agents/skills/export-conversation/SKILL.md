---
name: export-conversation
description: Use when exporting Antigravity / Gemini CLI JSONL conversation transcripts into structured Markdown documents with support for base+fork branches, thinking blocks, and tool calls
---

# Export Conversation Skill

## Overview
Provides a deterministic Python tool to export conversation transcripts (`transcript_full.jsonl`) into formatted Markdown files (`transcript-<id>.md`). It formats thinking blocks, tool calls, tool results, user requests, and agent responses, with support for base and divergent conversation branches.

## Quick Reference

```bash
# Export the current conversation (defaults to transcript-<id>.md in current working dir)
python3 .agents/skills/export-conversation/scripts/export_conversation.py \
  --conversation-id <CONVERSATION_ID>

# Export using explicit transcript path
python3 .agents/skills/export-conversation/scripts/export_conversation.py \
  --transcript /path/to/transcript_full.jsonl

# Export a branched conversation with its base lineage
python3 .agents/skills/export-conversation/scripts/export_conversation.py \
  --base-id <BASE_CONVERSATION_ID> \
  --conversation-id <BRANCH_CONVERSATION_ID>

# Export to a custom output path
python3 .agents/skills/export-conversation/scripts/export_conversation.py \
  --conversation-id <CONVERSATION_ID> \
  --output ./docs/transcript.md
```

## Features

1. **Lineage Stitching**: Combines base conversation history with divergent forked branches without losing earlier context.
2. **Thinking Blocks**: Wraps internal reasoning in collapsible `<details><summary>🧠 Thinking Process</summary>...</details>` blocks.
3. **Tool Invocations & Outputs**: Renders tool arguments and outputs in formatted, collapsible code sections with action summaries.
4. **User Turns**: Extracts `<USER_REQUEST>` cleanly while separating metadata and settings changes.
