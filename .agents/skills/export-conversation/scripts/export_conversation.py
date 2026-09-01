#!/usr/bin/env python3
"""
Deterministic Conversation Transcript Exporter for Antigravity / Gemini CLI.
Converts JSONL transcripts into clean, comprehensive Markdown logs with
support for base + divergence conversation branches, thinking blocks, tool calls,
tool outputs, and user/agent turns.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def find_brain_dir() -> Path:
    """Locate the default Antigravity / Gemini brain directory."""
    home = Path.home()
    return home / ".gemini" / "antigravity-cli" / "brain"


def load_transcript(path: Path) -> List[Dict[str, Any]]:
    """Load JSONL transcript file into a list of step dicts."""
    steps = []
    if not path.is_file():
        raise FileNotFoundError(f"Transcript file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    steps.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping corrupted JSON line: {e}", file=sys.stderr)
    return steps


def merge_branch_lineage(
    base_steps: List[Dict[str, Any]], branch_steps: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Merge a base conversation with a divergent branch.
    Finds the fork point using step_index and timestamps, then concatenates
    the base prefix with the branch's divergent suffix.
    """
    if not base_steps:
        return branch_steps
    if not branch_steps:
        return base_steps

    # If branch starts at step > 0, find base prefix
    first_branch_step = branch_steps[0].get("step_index", 0)
    if first_branch_step > 0:
        base_prefix = [s for s in base_steps if s.get("step_index", 0) < first_branch_step]
        return base_prefix + branch_steps

    return branch_steps


def format_user_content(content: str) -> str:
    """Clean and structure raw user request content."""
    req_match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", content, re.DOTALL)
    if req_match:
        user_req = req_match.group(1).strip()
    else:
        user_req = content.strip()

    meta_parts = []
    meta_match = re.search(r"<ADDITIONAL_METADATA>(.*?)</ADDITIONAL_METADATA>", content, re.DOTALL)
    if meta_match:
        meta_parts.append(f"**Metadata:**\n```\n{meta_match.group(1).strip()}\n```")

    settings_match = re.search(r"<USER_SETTINGS_CHANGE>(.*?)</USER_SETTINGS_CHANGE>", content, re.DOTALL)
    if settings_match:
        meta_parts.append(f"**Settings Change:**\n```\n{settings_match.group(1).strip()}\n```")

    formatted = user_req
    if meta_parts:
        formatted += "\n\n<details><summary>ℹ️ Additional Turn Context</summary>\n\n"
        formatted += "\n\n".join(meta_parts)
        formatted += "\n\n</details>"

    return formatted


def clean_arg_val(val: Any) -> Any:
    """Clean unescaped quotes or nested stringified JSON in tool args."""
    if isinstance(val, str):
        val_strip = val.strip()
        if val_strip.startswith('"') and val_strip.endswith('"') and len(val_strip) >= 2:
            try:
                return json.loads(val_strip)
            except Exception:
                return val_strip[1:-1]
        elif (val_strip.startswith('{') and val_strip.endswith('}')) or (
            val_strip.startswith('[') and val_strip.endswith(']')
        ):
            try:
                return json.loads(val_strip)
            except Exception:
                pass
    elif isinstance(val, dict):
        return {k: clean_arg_val(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [clean_arg_val(v) for v in val]
    return val


def render_step_to_markdown(step: Dict[str, Any]) -> str:
    """Render a single transcript step into Markdown."""
    step_idx = step.get("step_index", 0)
    source = step.get("source", "UNKNOWN")
    step_type = step.get("type", "UNKNOWN")
    created_at = step.get("created_at", "")
    content = step.get("content", "")
    thinking = step.get("thinking", "")
    tool_calls = step.get("tool_calls", [])

    time_str = f" • {created_at}" if created_at else ""
    md_parts = []

    # 1. USER INPUT
    if step_type == "USER_INPUT" or source == "USER_EXPLICIT":
        md_parts.append(f"\n---\n\n## 👤 User (Step {step_idx}{time_str})\n\n{format_user_content(content)}\n")
        return "".join(md_parts)

    # 2. MODEL THINKING
    if thinking:
        md_parts.append(
            f"\n<details><summary>🧠 Thinking Process (Step {step_idx})</summary>\n\n"
            f"{thinking.strip()}\n\n"
            f"</details>\n"
        )

    # 3. TOOL CALLS
    if tool_calls:
        for tc in tool_calls:
            name = tc.get("name", "unnamed_tool")
            args = tc.get("args", {})
            action_desc = ""
            if isinstance(args, dict):
                cleaned_args = {k: clean_arg_val(v) for k, v in args.items()}
                summary = cleaned_args.get("toolSummary", "")
                action = cleaned_args.get("toolAction", "")
                if summary:
                    action_desc = f" — *{summary}*"
                elif action:
                    action_desc = f" — *{action}*"
            else:
                cleaned_args = clean_arg_val(args)

            args_json = (
                json.dumps(cleaned_args, indent=2, ensure_ascii=False)
                if isinstance(cleaned_args, (dict, list))
                else str(cleaned_args)
            )
            md_parts.append(
                f"\n<details><summary>⚡ Tool Call: <code>{name}</code>{action_desc}</summary>\n\n"
                f"```json\n{args_json}\n```\n\n"
                f"</details>\n"
            )

    # 4. TOOL OUTPUT / GENERIC
    if step_type in ("GENERIC", "TOOL_OUTPUT") and content:
        md_parts.append(
            f"\n<details><summary>📥 Tool Output (Step {step_idx})</summary>\n\n"
            f"```text\n{content.strip()}\n```\n\n"
            f"</details>\n"
        )

    # 5. AGENT TEXT RESPONSE
    if step_type == "PLANNER_RESPONSE" and content:
        md_parts.append(f"\n## 🤖 Agent Response (Step {step_idx}{time_str})\n\n{content.strip()}\n")
    elif content and source == "MODEL" and step_type not in ("GENERIC", "TOOL_OUTPUT"):
        md_parts.append(f"\n## 🤖 Agent Response (Step {step_idx}{time_str})\n\n{content.strip()}\n")

    return "".join(md_parts)


def export_conversation(
    transcript_path: Path,
    base_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """Read transcript(s), render markdown, and write to output file."""
    branch_steps = load_transcript(transcript_path)
    base_steps = load_transcript(base_path) if base_path else []

    all_steps = merge_branch_lineage(base_steps, branch_steps)

    conv_id = transcript_path.parent.parent.parent.name
    if not output_path:
        output_path = Path.cwd() / f"transcript-{conv_id}.md"

    md_output = [
        f"# Conversation Transcript: `{conv_id}`\n\n",
        f"* **Exported At**: {datetime.now(timezone.utc).isoformat()}\n",
        f"* **Total Steps**: {len(all_steps)}\n",
        f"* **Source Path**: `{transcript_path}`\n",
    ]
    if base_path:
        md_output.append(f"* **Base Lineage Path**: `{base_path}`\n")
    md_output.append("\n---\n")

    for step in all_steps:
        rendered = render_step_to_markdown(step)
        if rendered:
            md_output.append(rendered)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_output))

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Export Antigravity / Gemini conversation transcripts to structured Markdown."
    )
    parser.add_argument("--conversation-id", "-c", help="Conversation UUID to export.")
    parser.add_argument("--transcript", "-t", type=Path, help="Explicit path to transcript_full.jsonl.")
    parser.add_argument("--base-transcript", "-b", type=Path, help="Base transcript path for forked conversations.")
    parser.add_argument("--base-id", help="Base conversation UUID for forked conversations.")
    parser.add_argument("--output", "-o", type=Path, help="Output Markdown file path (defaults to transcript-<id>.md).")

    args = parser.parse_args()

    brain_dir = find_brain_dir()

    # Resolve target transcript
    transcript_path = args.transcript
    if not transcript_path:
        if args.conversation_id:
            transcript_path = brain_dir / args.conversation_id / ".system_generated" / "logs" / "transcript_full.jsonl"
        else:
            print("Error: Specify either --conversation-id or --transcript", file=sys.stderr)
            sys.exit(1)

    base_path = args.base_transcript
    if not base_path and args.base_id:
        base_path = brain_dir / args.base_id / ".system_generated" / "logs" / "transcript_full.jsonl"

    out_file = export_conversation(transcript_path, base_path, args.output)
    print(f"✅ Successfully exported transcript to: {out_file}")


if __name__ == "__main__":
    main()
