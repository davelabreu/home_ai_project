# Roadmap

## BLUF
Core infrastructure is solid (v0.4.1). Next priorities: polish the dashboard UX, complete the data_gobbler trace inspector, and harden security. Wake-on-LAN and LLM-assisted data parsing are stretch goals.

---

## Current State (as of v0.4.1 — 2026-02-08)

### ✅ Done
- Ambidextrous web_monitor (PC + Jetson) with React frontend
- Docker Service Manager with one-click restart
- Jetson GPU/Power/Temp monitoring via jtop
- NVPModel power mode switching
- Ollama chat integration (qwen:1.8b)
- Hybrid network monitor (ARP + Nmap deep scan)
- Soft/Hard reboot from dashboard
- Homepage as unified entry point
- Netdata → InfluxDB telemetry pipeline
- data_gobbler hierarchical workbench with split-pane UI
- Auto-ingest workflow with deep dropdown selection

### 🔧 Known Issues
- `paramiko` NPM package in frontend package.json (wrong dependency, harmless)
- Legacy `templates/index.html` still exists (dead code)
- CORS origins hardcoded in Flask
- InfluxDB token hardcoded in config files
- No authentication on any endpoint

---

## Priority Queue

### P0 — Next Up
| Task | Service | Notes |
|---|---|---|
| Trace Inspector (rename/visibility) | data_gobbler | Offcanvas panel is stubbed, needs column-level controls |
| Clean up CORS | web_monitor | Make dynamic based on MONITOR_TARGET_HOST |
| Remove dead code | web_monitor | Delete legacy templates/index.html, remove paramiko from package.json |

### P1 — Short Term
| Task | Service | Notes |
|---|---|---|
| Multi-plot canvas | data_gobbler | FAB button to add independent plot cards |
| State persistence | data_gobbler | Save inspector settings to Project Plot Template JSON |
| Custom viz templates | data_gobbler | Per-log-type plot configurations |
| Dashboard theme toggle | web_monitor | ThemeProvider exists, needs UI toggle button |

### P2 — Medium Term
| Task | Service | Notes |
|---|---|---|
| Wake-on-LAN | web_monitor | Requires hardware (USB NIC or WoL-capable adapter). Pending purchase. |
| Secure remote access | infrastructure | VPN or reverse proxy for internet-facing access |
| Move secrets to env vars | infrastructure | InfluxDB token, any future API keys |
| Authentication layer | infrastructure | At minimum, basic auth on dashboard and API |

### P3 — Stretch / Exploratory
| Task | Service | Notes |
|---|---|---|
| LLM-assisted data parsing | data_gobbler | Use Jetson Ollama to auto-organize uploaded CSVs |
| Task offloading (Jetson → PC) | cross-service | Mechanism for Jetson to delegate heavy compute to PC |
| Custom Homepage widgets | homepage | Dynamic widgets driven by web_monitor API |
| Grafana integration | infrastructure | Alternative to custom dashboard for time-series viz |

---

## Milestone History

| Version | Date | Milestone |
|---|---|---|
| v0.4.1 | 2026-02-08 | Hierarchical Workbench & Split-Pane UI |
| v0.2.0 | 2026-02-08 | AI Workbench & Infrastructure |
| v0.1.0 | 2026-02-08 | Stable Dashboard Baseline |
