#!/usr/bin/env python3
"""
dump_all_notebooks.py

Consolidates all notebooks and block contents within a Deepnote Cloud project into
a single structured Markdown document.

BRING YOUR OWN ENVIRONMENT VARIABLE (BYO-Env) CONTRACT:
Strictly requires DEEPNOTE_TOKEN (and optionally DEEPNOTE_PROJECT_ID) in the environment.
Does NOT parse or load local .env files.
"""

import os
import sys
import argparse
import requests
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Consolidate all Deepnote project notebooks into a structured Markdown document."
    )
    parser.add_argument(
        "--project-id",
        "-p",
        default=os.getenv("DEEPNOTE_PROJECT_ID"),
        help="Deepnote Project UUID (defaults to DEEPNOTE_PROJECT_ID env var, or auto-discovers)."
    )
    parser.add_argument(
        "--output",
        "-o",
        default="/tmp/deepnote_project_megadump.md",
        help="Output file path (default: /tmp/deepnote_project_megadump.md)."
    )
    return parser.parse_args()

def resolve_project_id(token: str, candidate_id: str | None) -> tuple[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    
    if candidate_id:
        url = f"https://api.deepnote.com/v2/projects/{candidate_id}"
        res = requests.get(url, headers=headers, timeout=25)
        res.raise_for_status()
        p_data = res.json().get("project", {})
        return candidate_id, p_data.get("name", "Deepnote Project")
    
    # Auto-discovery via /v2/projects
    sys.stderr.write("No Project ID provided. Auto-discovering projects from Deepnote API...\n")
    url = "https://api.deepnote.com/v2/projects"
    res = requests.get(url, headers=headers, timeout=25)
    res.raise_for_status()
    projects = res.json().get("projects", [])
    
    if not projects:
        raise RuntimeError("No projects found in this Deepnote workspace.")
    
    # Match by repo name if possible
    repo_name = Path(os.getcwd()).name
    for p in projects:
        if p.get("name") == repo_name or repo_name in p.get("name", ""):
            sys.stderr.write(f"Matched project '{p.get('name')}' ({p.get('id')}) from repository name.\n")
            return p["id"], p.get("name", "Deepnote Project")
    
    # Default to first project
    chosen = projects[0]
    sys.stderr.write(f"Defaulting to first project '{chosen.get('name')}' ({chosen.get('id')}).\n")
    return chosen["id"], chosen.get("name", "Deepnote Project")

def main():
    args = parse_args()
    token = os.getenv("DEEPNOTE_TOKEN")

    if not token:
        sys.stderr.write("[FAIL FAST] Missing required environment variable: DEEPNOTE_TOKEN\n")
        sys.stderr.write("Please export DEEPNOTE_TOKEN or source your credentials before running.\n")
        sys.exit(1)

    try:
        project_id, project_name = resolve_project_id(token, args.project_id)
    except Exception as e:
        sys.stderr.write(f"[ERROR] Failed to resolve Deepnote project: {e}\n")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}
    project_url = f"https://api.deepnote.com/v2/projects/{project_id}"

    sys.stderr.write(f"Fetching project metadata from Deepnote API ({project_id})...\n")
    try:
        res = requests.get(project_url, headers=headers, timeout=25)
        res.raise_for_status()
        project_data = res.json().get("project", {})
    except Exception as e:
        sys.stderr.write(f"[ERROR] Failed to fetch project metadata: {e}\n")
        sys.exit(1)

    notebooks = project_data.get("notebooks", [])
    sys.stderr.write(f"Found {len(notebooks)} notebook(s) in project '{project_name}'.\n")

    output_path = Path(args.output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"# Deepnote Project Megadump: {project_name}\n\n")
        out.write(f"* **Project ID**: `{project_id}`\n")
        out.write(f"* **Total Notebooks**: {len(notebooks)}\n\n")
        out.write("---\n\n")

        for idx, nb in enumerate(notebooks, 1):
            nb_id = nb["id"]
            nb_name = nb["name"]
            sys.stderr.write(f"[{idx}/{len(notebooks)}] Fetching notebook '{nb_name}' ({nb_id})...\n")

            nb_url = f"https://api.deepnote.com/v2/notebooks/{nb_id}"
            try:
                nb_res = requests.get(nb_url, headers=headers, timeout=25)
                nb_res.raise_for_status()
                nb_data = nb_res.json().get("notebook", {})
            except Exception as e:
                sys.stderr.write(f"[WARNING] Failed to fetch notebook '{nb_name}' ({nb_id}): {e}\n")
                continue

            blocks = nb_data.get("blocks", [])

            out.write(f"# Notebook {idx}: `{nb_name}`\n\n")
            out.write(f"* **Notebook ID**: `{nb_id}`\n")
            out.write(f"* **Total Blocks**: {len(blocks)}\n\n")

            for b_idx, block in enumerate(blocks):
                b_id = block.get("id")
                b_type = block.get("type", "unknown")
                b_content = block.get("content") or ""
                b_meta = block.get("metadata") or {}

                var_name = b_meta.get("deepnote_variable_name")
                label = (
                    b_meta.get("deepnote_input_label")
                    or b_meta.get("deepnote_input_checkbox_label")
                    or b_meta.get("deepnote_button_title")
                )

                meta_info = []
                if var_name:
                    meta_info.append(f"Variable: `{var_name}`")
                if label:
                    meta_info.append(f"Label: `{label}`")

                meta_str = f" ({', '.join(meta_info)})" if meta_info else ""

                out.write(f"### Block {b_idx:02d} — `{b_type}`{meta_str}\n")
                out.write(f"<!-- Block ID: {b_id} -->\n\n")

                if b_type == "code":
                    out.write("```python\n")
                    out.write(b_content.strip() + "\n")
                    out.write("```\n\n")
                elif b_type in ("input-text", "input-textarea", "input-checkbox", "input-select"):
                    out.write("```text\n")
                    out.write(b_content.strip() + "\n")
                    out.write("```\n\n")
                elif b_type == "button":
                    out.write(f"> **Button**: `{label or 'Action'}`\n\n")
                elif b_type in ("markdown", "text-cell-h1", "text-cell-h2", "text-cell-p"):
                    out.write(b_content.strip() + "\n\n")
                else:
                    out.write("```text\n")
                    out.write(b_content.strip() + "\n")
                    out.write("```\n\n")

            out.write("\n---\n\n")

    sys.stderr.write(f"✅ Successfully exported {len(notebooks)} notebook(s) to: {output_path.resolve()}\n")

if __name__ == "__main__":
    main()
