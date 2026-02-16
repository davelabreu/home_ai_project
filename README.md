# Home AI Companion

A Docker-based home automation and monitoring system running on an NVIDIA Jetson (always-on) with a Main PC for heavy tasks.

## What It Does

- **Dashboard** (`web_monitor`) — Real-time monitoring of CPU, GPU, memory, network devices, Docker containers, and power modes. Flask backend + React frontend. Works on both the Jetson (local control) and PC (remote management).
- **Engineering Workbench** (`data_gobbler`) — Multi-project data ingestion and visualization platform for engineering analysis. Dash/Plotly with hierarchical CSV storage.
- **Legacy Analytics** (`data_analyzer`) — Earlier analytics service, maintenance mode only.
- **Supporting Services** — Ollama (local LLM), Netdata (telemetry), InfluxDB (metrics), Homepage (dashboard hub).

## Quick Start

### Deploy on Jetson
```bash
git clone <repo-url>
cp .env.example .env        # Edit with your settings
./deploy.sh                  # Interactive deployment menu
```

### Local Development (PC)
```bash
# Web Monitor frontend
cd web_monitor/frontend && npm install && npm run dev

# Any Python service
cd web_monitor  # or data_gobbler, data_analyzer
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && python3 app.py
```

## Network

| Host | IP | Role |
|---|---|---|
| Jetson | 192.168.1.11 | Always-on companion, runs all Docker services |
| Main PC | 192.168.1.2 | Development, heavy compute, remote management |

## Services & Ports

| Service | Port | URL |
|---|---|---|
| Dashboard | 8050 | `http://192.168.1.11:8050` |
| Data Analyzer | 8051 | `http://192.168.1.11:8051` |
| Data Gobbler | 8052 | `http://192.168.1.11:8052` |
| Homepage | 3000 | `http://192.168.1.11:3000` |
| Ollama | 11434 | `http://192.168.1.11:11434` |
| Netdata | 19999 | `http://192.168.1.11:19999` |
| InfluxDB | 8086 | `http://192.168.1.11:8086` |

## Documentation

All project documentation lives in [`docs/`](docs/README.md). Agent context files (`CLAUDE.md`, `GEMINI.md`) at the repo root point there.
