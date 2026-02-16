# Architecture Overview

## BLUF
Three Docker microservices on an NVIDIA Jetson (192.168.1.11) + a mirrored dashboard on Main PC (192.168.1.2). Flask backends, React/Dash frontends, all orchestrated via `docker-compose.yml`. The Jetson is always-on; the PC is for heavy tasks.

---

## System Topology

```
┌─────────────────────────────────────────────────────────┐
│  Main PC (192.168.1.2) — Windows                       │
│  ┌─────────────────────────────────┐                    │
│  │ web_monitor (dev mode)          │                    │
│  │ Flask :5000 + React frontend    │──── HTTP ────┐     │
│  │ MONITOR_TARGET_HOST=192.168.1.11│              │     │
│  └─────────────────────────────────┘              │     │
└───────────────────────────────────────────────────│─────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────┐
│  Jetson Nano (192.168.1.11) — Ubuntu/Docker             │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ dashboard     │  │ data_analyzer│  │ data_gobbler │  │
│  │ :8050→:5000   │  │ :8051→:8050  │  │ :8052→:8050  │  │
│  │ Flask+React   │  │ Dash/Plotly  │  │ Dash/Plotly  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ ollama       │  │ netdata      │  │ influxdb     │  │
│  │ :11434       │  │ :19999       │  │ :8086        │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌──────────────┐                                       │
│  │ homepage     │                                       │
│  │ :3000        │                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

## Port Map (Host → Container)

| Service | Host | Container | Tech |
|---|---|---|---|
| dashboard (web_monitor) | 8050 | 5000 | Flask + React |
| data_analyzer | 8051 | 8050 | Dash/Plotly |
| data_gobbler | 8052 | 8050 | Dash/Plotly |
| homepage | 3000 | 3000 | Homepage |
| ollama | 11434 | 11434 | Ollama |
| netdata | 19999 | 19999 | Netdata |
| influxdb | 8086 | 8086 | InfluxDB |

## Service Responsibilities

### web_monitor (Active Development)
- **Role**: Primary dashboard and control plane
- **Design**: "Ambidextrous" — detects OS and adapts behavior
  - **On Windows (PC)**: Management console. Forwards requests to Jetson via HTTP
  - **On Linux (Jetson)**: Data source. Executes local commands (jtop, dbus-send, docker)
- **Stack**: Flask backend, React 19 + Tailwind 4 + Shadcn UI frontend, Vite (rolldown-vite)
- **Key APIs**: system info, network status, GPU metrics, Docker management, Ollama chat, power mode, reboot

### data_gobbler (Active Development — v0.4.1)
- **Role**: Engineering data analysis workbench
- **Design**: Multi-page Dash app with split-pane UI
- **Key Pattern**: Hidden DOM rule — all dynamic components pre-rendered, toggled with CSS
- **Data Model**: `projects/[project_id]/[subsystem]/[test]/ingest_*.csv`

### data_analyzer (Maintenance Mode — v0.2.2)
- **Role**: Legacy analytics service
- **Rule**: Critical bug fixes only. Active development moved to data_gobbler

## Key Design Decisions

| Decision | Rationale | Reference |
|---|---|---|
| Ambidextrous web_monitor | Single codebase serves both PC dashboard and Jetson host | ADR-001 |
| Hidden DOM rule (Dash) | Prevents Dash callback crashes from missing Input IDs | ADR-002 |
| HTTP forwarding (no SSH from PC) | Simplicity: PC makes HTTP calls, Jetson handles local commands | ADR-003 |
| docker-compose as source of truth | Single file defines all Jetson state | ADR-004 |
| jtop over tegrastats parsing | More reliable, maintained library for Jetson metrics | ADR-005 |

## Data Flow Patterns

### PC → Jetson Control Flow
```
PC Frontend → PC Flask (/api/remote_*) → HTTP → Jetson Flask (/api/local_*) → subprocess/jtop/docker
```

### Ingestion Flow (data_gobbler)
```
CSV Upload → base64 → Ingest Wizard → Processor (optional) → DataManager.save → filesystem
                                                                    ↓
                                                          last-ingested-file (dcc.Store)
                                                                    ↓
                                                          Auto-redirect + deep selection
```
