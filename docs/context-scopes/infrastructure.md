# Context Scope: Infrastructure

> Load this file when working on Docker, deployment, networking, or cross-service concerns.

## Key Files
```
├── docker-compose.yml          # Single source of truth for all Jetson services
├── deploy.sh                   # Interactive deployment menu
├── web_monitor/Dockerfile      # Multi-stage: Node 20 Alpine → NVIDIA L4T base
├── data_analyzer/Dockerfile    # python:3.10-slim
├── data_gobbler/Dockerfile     # python:3.10-slim
├── homepage/config/            # services.yaml, settings.yaml, widgets.yaml, docker.yaml
├── netdata/config/             # exporting.conf (→ InfluxDB)
└── .env                        # MONITOR_TARGET_HOST, etc.
```

## Docker Compose Services Summary
| Service | Image | Volumes (Notable) | Special |
|---|---|---|---|
| dashboard | Custom (L4T) | dbus, docker.sock, jtop.sock, SSH key, tegrastats, nvpmodel, /sys, /dev | `runtime: nvidia` |
| ollama | ollama/ollama:latest | ~/.ollama | `OLLAMA_KEEP_ALIVE=-1` |
| netdata | netdata/netdata:latest | /proc, /sys, docker.sock (ro) | SYS_PTRACE, SYS_ADMIN, pid: host |
| influxdb | influxdb:latest | Named volumes | Init credentials in env |
| data_analyzer | Custom (slim) | ./data_analyzer/projects | |
| data_gobbler | Custom (slim) | ./data_gobbler/projects | |
| homepage | ghcr.io/gethomepage/homepage | ./homepage/config, docker.sock (ro) | HOMEPAGE_ALLOWED_HOSTS |

## deploy.sh Menu
1. **Full System Reset** — kill port 11434, clear caches, restart Docker, rebuild all, prime Ollama
2. **Restart All EXCEPT Ollama** — git pull, rebuild non-AI services only
3. **Restart Individual Container** — sub-menu to pick one
4. **Restart/Prime Ollama Only** — clear port, restart, warm-load qwen:1.8b

## Netdata → InfluxDB Pipeline
- Netdata exports via `exporting.conf` to InfluxDB API v2
- Org: `home_ai`, Bucket: `jetson_metrics`
- Token in config (should be moved to env vars — security TODO)

## Network Topology
- Jetson: 192.168.1.11 (always-on)
- Main PC: 192.168.1.21
- All services accessible on LAN via Jetson IP + host port
- Homepage at :3000 is the unified entry point

## Security TODOs
- [ ] InfluxDB token is hardcoded in `netdata/config/exporting.conf` and `docker-compose.yml`
- [ ] CORS origins in `web_monitor/app.py` are hardcoded
- [ ] No authentication on any service (LAN-only assumption)
- [ ] SSH private key mounted read-only but path is in docker-compose.yml

## Common Operations
```bash
# Rebuild everything except Ollama (most common deploy)
docker compose up -d --build $(docker compose config --services | grep -v ollama)

# Check all services
docker compose ps

# View logs for a specific service
docker compose logs -f dashboard

# Full nuclear reset
./deploy.sh  # Option 1

# Quick test after changes
docker compose restart dashboard
```
