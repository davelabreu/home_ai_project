# Context Scope: web_monitor

> Load this file when working on the dashboard (Flask backend or React frontend).

## Service Identity
- **Status**: Active Development
- **Container**: `home_ai_dashboard`
- **Ports**: Host 8050 → Container 5000
- **Stack**: Flask + React 19 + Tailwind 4 + Shadcn UI + Vite (rolldown-vite)

## Architecture Summary
- Flask backend (`app.py`) serves React build from `frontend/dist/` AND exposes REST APIs
- "Ambidextrous": checks `sys.platform` and `MONITOR_TARGET_HOST` to decide behavior
- **PC mode** (Windows): Forwards requests to Jetson via HTTP. No SSH, no local system commands
- **Jetson mode** (Linux/Docker): Executes locally via subprocess, jtop, docker socket, dbus-send

## Key Files
```
web_monitor/
├── app.py                      # Flask backend — ALL API routes
├── device_names.json           # MAC → friendly name mapping
├── requirements.txt            # Flask, psutil, requests, dotenv, Flask-Cors, jetson-stats, docker
├── Dockerfile                  # Multi-stage: Node builder → L4T Python runtime
├── scripts/get_stats.py        # jtop-based Jetson metric collector
└── frontend/
    ├── src/
    │   ├── App.tsx             # Root component, layout, state orchestration
    │   ├── components/         # One file per card/widget
    │   │   ├── SystemInfoCard.tsx
    │   │   ├── GpuInfoCard.tsx
    │   │   ├── NetworkStatusCard.tsx
    │   │   ├── DockerServiceManager.tsx
    │   │   ├── PowerModeCard.tsx
    │   │   ├── ChatCard.tsx
    │   │   └── FaviconChanger.tsx
    │   ├── hooks/              # One hook per data source
    │   │   ├── useSystemInfo.ts
    │   │   ├── useGpuInfo.ts
    │   │   ├── useNetworkStatus.ts
    │   │   ├── useDockerServices.ts
    │   │   ├── usePowerMode.ts
    │   │   └── useConfig.ts
    │   └── components/ui/      # Shadcn primitives (button, card, input, progress)
    ├── index.html
    ├── vite.config.js
    ├── tailwind.config.js
    ├── tsconfig.json
    └── package.json
```

## API Endpoints (app.py)
| Method | Route | Behavior |
|---|---|---|
| GET | `/api/local_system_info` | CPU, memory, disk, uptime via psutil |
| GET | `/api/remote_system_info` | Forwards to MONITOR_TARGET_HOST |
| GET | `/api/local_network_status` | ARP cache parse (fast) |
| GET | `/api/local_network_scan` | Nmap deep scan (slow) |
| GET | `/api/remote_network_status` | Forwards to MONITOR_TARGET_HOST |
| GET | `/api/jetson_gpu_info` | jtop via get_stats.py (Jetson) or forwards (PC) |
| GET | `/api/docker_services` | Lists containers via Docker socket |
| POST | `/api/docker_services/restart` | Restarts container by name (with self-restart safety) |
| POST | `/api/command/reboot` | Soft (Docker restart) or Hard (dbus-send) reboot |
| GET/POST | `/api/power_mode` | NVPModel query/set |
| POST | `/api/chat` | Proxy to Ollama |
| GET | `/api/config` | Returns MONITOR_TARGET_HOST status to frontend |

## CORS Configuration
Currently allows: `http://localhost:5000`, `http://192.168.1.21:5000`

## Environment Variables
- `MONITOR_TARGET_HOST` — Remote Jetson IP (empty = local-only mode)
- `MONITOR_TARGET_PORT` — Remote port (default 5000)
- `OLLAMA_HOST` — Ollama endpoint (default `http://ollama:11434` in Docker)
- `SSH_USERNAME`, `SSH_PRIVATE_KEY_PATH` — For Jetson container (mounted via docker-compose)

## Build & Test
```bash
# Frontend dev
cd web_monitor/frontend && npm run dev

# Frontend production build
cd web_monitor/frontend && npm run build

# Backend dev (local)
cd web_monitor && python3 app.py

# Docker rebuild
docker compose up -d --build dashboard
```

## Current Gotchas
- `paramiko` is listed in frontend `package.json` as a dependency — this is wrong (npm package, not the Python lib). Harmless but confusing.
- Legacy `templates/index.html` still exists (Pico.css version). Flask serves the React build, not this file.
- CORS is hardcoded — needs to be dynamic based on `MONITOR_TARGET_HOST`.
