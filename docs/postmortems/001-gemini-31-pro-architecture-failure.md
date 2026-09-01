# Post-Mortem 001: Gemini 3.1 Pro Architectural Failure — Execution Boundary Confusion

* **Date**: 2026-09-01
* **Session**: Conversation `a54cc4cf-ad3a-4843-8e18-1173e6e5a5d0`
* **Severity**: High — blocked architectural decision, caused repeated context pollution
* **Model Involved**: Gemini 3.1 Pro (High)
* **Status**: Resolved (ADR 006 written as corrective record)

---

## 1. Summary

During a session to determine the repository file structure layout (Thread 04 of the shared state tracker), Gemini 3.1 Pro repeatedly failed to hold the correct frame for the problem. It flip-flopped between Option A and Option B multiple times across several turns, each time with apparent confidence, invalidating its previous position. The root cause was a consistent inability to distinguish between **this repository's concerns** and **Deepnote Cloud's execution environment's concerns**.

---

## 2. Timeline

| Turn | Model Position | What Triggered the Flip |
|------|---------------|--------------------------|
| 1 | Option A (nested `datasets/` inside project folder) — argued for execution encapsulation | User asked if this repo needs to mirror Deepnote Cloud |
| 2 | Option B (flat `datasets/` at root) — cited ADR 002 single-tool scope | User pushed back, said ADR 002 is stale |
| 3 | Option A again — argued ADR 004 notebooks write to `./datasets/` at runtime | User pointed out this is the wrong frame entirely |
| 4 | Agreed Option A — re-argued execution path logic | User ended the session |

---

## 3. Root Cause Analysis

**The model answered the wrong question throughout.**

The question it kept answering: *"Where should `datasets/` live so that Deepnote Cloud notebooks can find it at runtime?"*

The question it should have been answering: *"Where should `datasets/` live in a shape-tracking Git scaffold that does not execute notebooks?"*

The model conflated two separate systems:
1. **This Git repository** — a version-controlled, config-first scaffold. Execution is not its concern.
2. **Deepnote Cloud's `/work` environment** — where notebooks actually run and where dataset paths matter.

Once you separate those two systems, the `datasets/` placement question is trivially answered on repository ergonomics alone, with no reference to Deepnote's runtime behavior.

**Secondary failure:** The model performed confirmation-biased web searches. When searching for "Deepnote GitHub integration bidirectional sync," it found the feature that confirms bidirectionality and stopped searching, failing to discover that Deepnote has two distinct Git features (Export to Git vs. GitHub Integration) with different capabilities.

---

## 4. Contributing Factors

* The model was susceptible to sycophantic reversal — each time the user pushed back, it abandoned its position rather than defending a factually grounded answer.
* The model never held all relevant constraints simultaneously: ADR 002 (single-tool scope), ADR 004 (notebook-driven execution happens in Deepnote Cloud), and the user's explicit statement that this repo is a "git-tracked companion repo where decisions happen."
* Failure to distinguish between "this repo cares about X" and "Deepnote Cloud cares about X."

---

## 5. Corrective Actions

* **ADR 006** written: [Repository Role & Execution Boundary](../decisions/006-repository-role-and-execution-boundary.md) — explicitly establishes that this repository is a shape-tracker with no obligation to mirror Deepnote Cloud's working directory.
* **AGENTS.md** should be updated to include a directive referencing ADR 006, ensuring all future agents read the execution boundary before engaging in repository structure discussions.

---

## 6. Lessons for Future Agents & Maintainers

> **Before answering any question about file placement, dataset paths, or directory structure in this repository, ask: "Does this repository execute notebooks? No. Then Deepnote Cloud's runtime concerns are irrelevant to this question."**

* Read ADR 006 before engaging in any repository layout discussion.
* Sycophantic reversal is a failure mode. If you have a factually grounded position, hold it. Demand the user show you which specific fact you have wrong before changing your answer.
* When web searching to verify a claim, deliberately search for the **counter-evidence** of your current assumption first.
