# Architecture Decision Records

> **Purpose**: Capture the *why* behind design choices so future sessions (human or agent) don't accidentally undo good decisions.

## How to Use This

Before refactoring or changing an established pattern, check if there's an ADR explaining why it exists. If you're making a new significant decision, add an entry.

### ADR Template (copy to `docs/adr/NNN-title.md`)
```markdown
# ADR-NNN: Title

**Status**: Accepted | Superseded | Deprecated
**Date**: YYYY-MM-DD
**Context**: What problem were we solving?
**Decision**: What did we decide?
**Consequences**: What are the trade-offs?
```

---

## Decision Log

| ID | Decision | Status | Date |
|---|---|---|---|
| 001 | Ambidextrous web_monitor (single codebase, OS detection) | Accepted | 2026-02-08 |
| 002 | Hidden DOM rule for Dash callbacks | Accepted | 2026-02-08 |
| 003 | HTTP forwarding from PC (no SSH/Paramiko) | Accepted | 2026-02-08 |
| 004 | docker-compose.yml as single source of truth | Accepted | 2026-02-08 |
| 005 | jtop library over tegrastats parsing | Accepted | 2026-02-08 |
| 006 | Hierarchical CSV storage over database | Accepted | 2026-02-08 |
| 007 | Separate Dash services (analyzer vs gobbler) | Accepted | 2026-02-08 |
| 008 | React + Shadcn over plain HTML dashboard | Accepted | 2026-02-08 |

---

## ADR-001: Ambidextrous web_monitor
**Status**: Accepted  
**Context**: We needed a dashboard that works both as a local Jetson control panel AND as a remote management console on the PC.  
**Decision**: Single Flask codebase that checks `sys.platform` and `MONITOR_TARGET_HOST` to determine behavior. PC mode forwards HTTP requests; Jetson mode executes locally.  
**Consequences**: (+) One codebase to maintain. (+) Same API surface everywhere. (-) Platform-specific branches in route handlers. (-) Must test both code paths.

## ADR-002: Hidden DOM Rule
**Status**: Accepted  
**Context**: Dash callbacks crash with "Nonexistent object" errors if an `Input` ID is missing from the layout.  
**Decision**: All dynamic components are declared in `app.layout` at boot and toggled with `style={'display': 'none'}`. Never conditionally render components with `Input` IDs.  
**Consequences**: (+) No callback crashes. (+) Predictable layout. (-) Larger initial DOM. (-) Must remember to toggle visibility, not render/unrender.

## ADR-003: HTTP Forwarding (No SSH from PC)
**Status**: Accepted  
**Context**: Originally considered Paramiko SSH from PC to Jetson for remote commands.  
**Decision**: Removed all SSH/Paramiko. PC makes HTTP calls to Jetson's Flask API. Jetson handles local execution via `subprocess`, `dbus-send`, Docker socket.  
**Consequences**: (+) Much simpler. (+) No SSH key management on PC. (+) Same API works for any client. (-) Requires Jetson's Flask app to be running for any remote control.

## ADR-004: docker-compose as Source of Truth
**Status**: Accepted  
**Context**: Needed a single, declarative way to define all Jetson services.  
**Decision**: Everything runs via `docker-compose.yml`. `deploy.sh` wraps common operations. No systemd services for app code.  
**Consequences**: (+) One file to understand the whole system. (+) Easy rebuild/redeploy. (-) Docker overhead on constrained Jetson hardware.

## ADR-005: jtop over tegrastats
**Status**: Accepted  
**Context**: Originally parsed `tegrastats` output with regex, which was fragile.  
**Decision**: Use the `jetson-stats` (jtop) Python library via `scripts/get_stats.py`.  
**Consequences**: (+) Maintained upstream library. (+) Structured data output. (-) Requires jtop service running on host. (-) Socket mount needed in Docker.

## ADR-006: Hierarchical CSV Storage
**Status**: Accepted  
**Context**: data_gobbler needed to organize engineering data by project, subsystem, and test.  
**Decision**: Flat filesystem: `projects/[project_id]/[subsystem]/[test]/ingest_*.csv`. DataManager class handles all path logic.  
**Consequences**: (+) No database dependency. (+) Easy to inspect/backup. (+) Docker volume mount = persistence. (-) No query engine. (-) Globbing at scale could slow down.

## ADR-007: Separate Dash Services
**Status**: Accepted  
**Context**: data_analyzer was the original workbench. data_gobbler is the v2 rewrite with a modular architecture.  
**Decision**: Keep both running. data_analyzer in maintenance mode, data_gobbler in active development.  
**Consequences**: (+) No risk of breaking stable service during v2 development. (-) Two containers consuming resources on Jetson. Will eventually deprecate data_analyzer.

## ADR-008: React + Shadcn for Dashboard
**Status**: Accepted  
**Context**: Original dashboard was vanilla HTML/JS with Pico.css (still in `templates/index.html`).  
**Decision**: Migrated to React 19 + Vite + Tailwind 4 + Shadcn UI. Flask serves built React app.  
**Consequences**: (+) Component-based, maintainable UI. (+) Dark mode support. (+) Rich component library. (-) Build step required. (-) More complex than plain HTML.
