# Project Knowledge Framework

> **Purpose**: Give any agentic coding tool (Claude Code, Gemini CLI, Cursor, etc.) the minimum context it needs to make good decisions — fast.

## How This Framework Works

Every agentic session should start by reading **two things**:

1. **The root `CLAUDE.md`** (or `GEMINI.md`) — system-wide architecture & commands
2. **The relevant Context Scope** from `docs/context-scopes/` — scoped to the service you're working on

This keeps the context window tight and relevant instead of dumping the entire repo into every session.

## Document Index

| Document | Purpose | When to Read |
|---|---|---|
| `CLAUDE.md` | Root project context: architecture, ports, build commands | Every session |
| `docs/ARCHITECTURE.md` | Deep system design, data flow, deployment topology | When making cross-service changes |
| `docs/CONVENTIONS.md` | Coding standards, naming, patterns, PR rules | When writing new code |
| `docs/DECISIONS.md` | Why things are the way they are (ADR log) | When tempted to refactor something |
| `docs/ROADMAP.md` | Current priorities and next milestones | When choosing what to work on |
| `docs/SESSION_GUIDE.md` | How to run an effective agentic coding session | Before every session |
| `docs/context-scopes/` | Per-service context files for focused work | When working on a specific service |
| `docs/adr/` | Individual Architecture Decision Records | When making or reviewing design choices |

## Quick Start for Agents

```
You are working on the home_ai_project. Before doing anything:
1. Read CLAUDE.md for system overview
2. Read docs/context-scopes/<service>.md for the service you're modifying
3. Read docs/CONVENTIONS.md if writing new code
4. Check docs/DECISIONS.md if you're about to change an existing pattern
```
