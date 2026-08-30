# ADR 001: MCP Remote Client Header Authentication & Dynamic Secret Injection

* **Status**: Accepted
* **Date**: 2026-08-30
* **Category**: Diátaxis Explanation / Architectural Decision Record (ADR)
* **Domain**: Agent Tooling & Secret Management

---

## 1. Context & Problem Statement

When connecting agentic coding harnesses to remote Model Context Protocol (MCP) servers (such as Deepnote's SSE/HTTP MCP server at `https://deepnote.com/mcp`), client authentication requires an HTTP `Authorization: Bearer <TOKEN>` header.

During initial setup, the MCP server consistently returned `401 Unauthorized` despite the token being defined in local `.env` files.

---

## 2. Root Cause Analysis

Two independent failure modes caused the authentication breakdown:

1. **Subprocess Environment Isolation**: Sourcing a standard `.env` file containing `KEY=VALUE` (without `export`) creates shell-local variables in interactive bash sessions. Background daemon processes (such as the Language Server runner) do not inherit unexported shell variables.
2. **Client Header String Literal Evaluation**: The remote MCP client parses `mcp_config.json` statically. When `"Authorization": "Bearer ${DEEPNOTE_TOKEN}"` was provided, the client sent the literal string `"${DEEPNOTE_TOKEN}"` across HTTP rather than performing runtime environment variable interpolation. Deepnote rejected this literal token as invalid.

---

## 3. Decision

1. **Template Pattern for Secret Management**:
   * Establish the MCP config template (`.agents/mcp_config.json.template`) using Doppler substitution syntax (`{{.DEEPNOTE_TOKEN}}`).
   * This template is version-controlled and contains zero plaintext credentials.
2. **Gitignored Local Active Config**:
   * The resolved local config (`.agents/mcp_config.json`) containing the active bearer token is strictly gitignored.
3. **Dynamic Injection via Doppler / Environment**:
   * Active credentials are populated via Doppler (`doppler secrets substitute`) or exported prior to daemon execution, preventing static secrets from ever being committed to a public repository.

---

## 4. Consequences

* **Positive**: Eliminates risk of secret leaks in public Git repositories.
* **Positive**: Provides reproducible onboarding for developers using centralized secret management (Doppler).
* **Negative**: Requires generating `.agents/mcp_config.json` locally before the MCP client can connect.
