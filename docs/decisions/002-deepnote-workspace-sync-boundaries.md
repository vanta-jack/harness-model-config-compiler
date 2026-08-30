# ADR 002: Deepnote Workspace Synchronization Boundaries & Repository Isolation

* **Status**: Accepted
* **Date**: 2026-08-30
* **Category**: Diátaxis Explanation / Architectural Decision Record (ADR)
* **Domain**: Cloud Sync & Workspace Taxonomy

---

## 1. Context & Problem Statement

Deepnote organizes cloud assets into an organization-wide **Workspace** consisting of multiple category folders (`Apps`, `Data pipelines`, `Agents`, `Explorations`) and dozens of independent projects.

During local initialization, executing `deepnote sync deepnote --all-files` mirrored the *entire* Deepnote organization into the local directory, pulling unrelated projects (`👋 Welcome`, `Daily stock price dashboard`, `laboratory`) into this single-tool Git repository.

---

## 2. Root Cause Analysis

* The CLI command `deepnote sync <dir>` operates as an **organization-level backup and mirror tool**. It downloads all projects across all workspace folders by default.
* In contrast, this Git repository (`model-config-crafter`) represents a **single, standalone software tool**, not a monorepo for the user's entire cloud account.
* Running untargeted workspace syncs pollutes project-specific Git trees with external exploratory notebooks and credentials.

---

## 3. Decision: Strict Scope Isolation (Pattern 1)

1. **Adoption of Pattern 1 (Single Project Scope)**:
   * This repository tracks *only* the `model-config-compiler` project located in the `Apps` folder of Deepnote.
2. **Prohibition of Workspace-Level Syncing**:
   * Agents and developers must **never run untargeted `deepnote sync` commands** directly into the Git repository root.
3. **Direct MCP Interaction**:
   * Development and real-time block updates must target the specific Deepnote Project ID directly via Deepnote MCP tools (`update_block`, `create_block`, `get_notebook`) rather than pulling full workspace archives.

---

## 4. Consequences

* **Positive**: The Git repository remains completely clean and isolated from unrelated cloud experiments.
* **Positive**: Multiple developers or automated agents can work on the compiler without risking synchronization conflicts across other workspace projects.
* **Negative**: Workspace-wide backups must be maintained in a separate dedicated backup directory outside this repository.
