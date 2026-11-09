# Agent Operational Guidelines & Unified Control Plane Contract (AGENTS.md)

This repository adheres to the Unified Agent Control Plane standards. All automated agents (Antigravity, Claude Code, OpenCode, Hermes) and human engineers must strictly abide by the following 5 operational invariants:

---

## 1. Step 0 Intake Discipline & Pre-Flight Verification
* **Pre-Flight Inspection**: Never write speculative code or make changes before inspecting repository structure, package manifests (`package.json`, `go.mod`, `pyproject.toml`), and existing configuration.
* **Invariant & Policy Check**: Verify `.agent/skills-policy.json` to confirm authorized skills and domain profile.
* **Test Baseline**: Verify existing tests (`npm test`, `pytest`, `go test ./...`) before initiating any new phase.

## 2. Local Metal Coprocessor Routing (Apple Silicon First)
* **Zero-Cost On-Device Offload**: Prioritize local Apple Silicon inference via `local-ai-coprocessor` MCP tools before dispatching requests to cloud LLMs:
  - Tool/Function Routing & Intent Filtering (`local_tool_route`) — sub-10ms latency, $0.00 cloud spend.
  - Structured Data Extraction (`local_extract`) from error traces, logs, and ASTs.
  - Calibrated Binary & Typed Decisions (`local_typed_decision`) for gate evaluations.
  - Text & Code Embeddings / Reranking (`local_embed`, `local_vector_rank`) using EmbeddingGemma 2 BF16.
  - Offline Code Drafting & Diff Summaries (`local_generate`) using Gemma 2B MLX.
* **Cloud Fallback**: Only route to cloud models for complex multi-file reasoning, high-level planning, or synthesis beyond local parameter scale.

## 3. Session Mount Usage via `skills_resolver.py`
* **Zero Repo Bloat**: Do NOT commit skills directly into repository source trees. All skills are mounted dynamically into `.agent/session_skills/<session_id>/` from the central catalog (`~/.gemini/skills`).
* **Session Mount Invariants**:
  - Mount via CLI: `python3 ~/.gemini/skills/scripts/skills.py mount <skill> --session <id>`
  - Automatic TTL: Ephemeral session mounts expire after 8 hours (`session_ttl_hours: 8`).
  - Prune expired mounts: `python3 ~/.gemini/skills/scripts/skills.py prune-sessions --apply`
  - Cryptographic Verification: Session mounts are verified via SHA-256 integrity hashes.
* **Strict Git Exclusion**: `.agent/session_skills/` is git-ignored and never committed to version control.

## 4. GWE Continuous Checkpointing (Gated Workflow Engine)
* **State Machine Integrity**: Multi-phase workflows must record progression in `.workflow_state/state.json` with HMAC verification (`.state.hmac`) and cryptographic nonce (`.nonce`).
* **Deterministic Phase Gates**:
  - Phase transitions require passing explicit verification gates (`gate0` through `gateN`).
  - Never bypass verification gates. Always run linters and test suites (`lint-and-validate`, `testing-protocol`).
* **Crash-Proof Recovery**: If interrupted, reload state from `.workflow_state/state.json` rather than restarting workflows from scratch.

## 5. 5,000,000 Token FinOps Hard Circuit-Breaker
* **Hard Budget Ceiling**: Cumulative token consumption is strictly capped at **5,000,000 tokens** per session and per project.
* **Tripwire Enforcement**: When telemetry detects token consumption approaching or exceeding 5,000,000 tokens across harnesses (Antigravity, Claude Code, OpenCode):
  - Execution automatically halts with a FinOps tripwire alert.
  - No automated retries, recursive agent loops, or speculative fan-outs are permitted.
* **Operator Override Required**: Resuming execution beyond 5,000,000 tokens requires an explicit human operator override:
  `python3 ~/.agent-mesh/scripts/circuit_breaker.py override --session <id> --reason "<justification>"`
