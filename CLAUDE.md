# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start for Agents

**Before writing any code**, load the relevant context:
1. Read this file (system overview)
2. Read `docs/context-scopes/<service>.md` for the service you're modifying
3. Read `docs/CONVENTIONS.md` if writing new code
4. Check `docs/DECISIONS.md` if changing an existing pattern
5. Follow `docs/SESSION_GUIDE.md` for session discipline

Full documentation index: `docs/README.md`

## Project Overview

Home AI Companion — a Docker-based home automation system running on an NVIDIA Jetson (192.168.1.11, always-on) with a Main PC (192.168.1.2) for heavy tasks. Three main microservices plus supporting infrastructure, all orchestrated via `docker-compose.yml`.

## Architecture

**web_monitor** — Flask backend + React/Vite/TypeScript frontend. The Flask app (`web_monitor/app.py`) serves the built React app from `frontend/dist` and exposes REST APIs for network status, Jetson GPU info, Docker service management, Ollama chat, and remote reboot. "Ambidextrous" design: adapts behavior for Windows (dev) vs Linux/Docker (production).

**data_gobbler** — Active development. Dash/Plotly engineering workbench (v0.4.1). Multi-page app using `dash.page_registry`. Key pattern: modular components (`components/`), utilities (`utils/`), and per-page layouts (`pages/`). Data is hierarchical: `projects/[project_id]/[subsystem]/[test]/ingest_*.csv`. Uses split-pane UI with pattern-matching callbacks (`MATCH`, `ALL`) for dynamic plot cards. All dynamic components are rendered at boot and toggled with CSS visibility (hidden DOM rule).

**data_analyzer** — Maintenance mode. Earlier Dash/Plotly analytics service, kept stable at v0.2.2.

**Supporting services**: Ollama (local LLM, port 11434), Netdata (telemetry, port 19999), InfluxDB (metrics, port 8086), Homepage (dashboard, port 3000).

## Port Mapping (host → container)

| Service | Host Port | Container Port |
|---|---|---|
| dashboard (web_monitor) | 8050 | 5000 |
| data_analyzer | 8051 | 8050 |
| data_gobbler | 8052 | 8050 |
| Homepage | 3000 | 3000 |
| Ollama | 11434 | 11434 |
| Netdata | 19999 | 19999 |
| InfluxDB | 8086 | 8086 |

## Build & Run Commands

### Full Docker Deployment (on Jetson)
```bash
./deploy.sh                          # Interactive menu: full reset, selective rebuild, etc.
docker compose up --build -d         # Build and start all services
docker compose up -d --build $(docker compose config --services | grep -v ollama)  # Rebuild all except Ollama
```

### Web Monitor Frontend (local dev)
```bash
cd web_monitor/frontend
npm install
npm run dev       # Vite dev server
npm run build     # Production build → frontend/dist/
npm run lint      # ESLint
```

### Python Services (local dev)
```bash
cd web_monitor    # or data_gobbler, data_analyzer
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv/Scripts/activate
pip install -r requirements.txt
python3 app.py
```

## Key Conventions

- **Dash callbacks**: Use `@callback` decorators with pattern-matching IDs (`{"type": "...", "index": MATCH}`). All dynamic UI elements are pre-rendered and hidden, not created dynamically.
- **Data storage**: CSV files under `projects/` directories with structure `project_id/subsystem/test/ingest_YYYY-MM-DD_HH-MM.csv`.
- **Frontend stack**: React 19, Tailwind CSS 4, Shadcn UI components, Lucide icons. Vite is aliased to rolldown-vite.
- **Python style**: Flask for web_monitor, Dash+Bootstrap (DARKLY theme) for data services. Each service has its own `requirements.txt` and `Dockerfile`.
- **Environment**: `.env` file for `MONITOR_TARGET_HOST`, `MONITOR_TARGET_PORT`, `SSH_USERNAME`, `SSH_PRIVATE_KEY_PATH`. See `.env.example`.
- **Git**: Semantic commits on `master` branch. Feature branching for larger work.

## Documentation Framework

```
docs/
├── README.md              # Index — start here
├── ARCHITECTURE.md        # System topology, data flows, service responsibilities
├── CONVENTIONS.md         # Coding standards, naming, patterns
├── DECISIONS.md           # Architecture Decision Records (ADR) log
├── ROADMAP.md             # Current priorities and next milestones
├── SESSION_GUIDE.md       # How to run disciplined agentic coding sessions
├── adr/                   # Individual ADR files
│   └── TEMPLATE.md        # Copy this for new decisions
└── context-scopes/        # Per-service context (load one per session)
    ├── web_monitor.md     # Dashboard/Flask/React work
    ├── data_gobbler.md    # Engineering workbench work
    └── infrastructure.md  # Docker/deploy/networking work
```
