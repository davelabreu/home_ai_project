# Home AI Companion Project

This `README.md` provides a high-level overview of the entire `home_ai_project`. For details on specific components, please refer to their respective README files.

## Project Structure

*   `README.md`: High-level overview, vision, and roadmap.
*   `scripts/`: Utility scripts, including `get_stats.py` for hardware metrics and `ollama_chat.py`.
*   `web_monitor/`: Ambidextrous web application (Flask/React) for monitoring and **service management**.
*   `data_analyzer/`: Dash Plotly microservice for data visualization.
*   `docker-compose.yml`: Unified orchestration for all Jetson services.

## Vision
To create a robust, simple home automation and AI companion system. The Jetson serves as the "Always-On" host and service manager, while the Main PC handles "Brain-Crunching" AI tasks. The system prioritizes Docker-centric management and straightforward, open-source-driven integrations.

## Hardware Components
*   **Jetson (Always-On Companion):**
    *   IP Address: 192.168.1.11
    *   Purpose: Local AI (QWEN), hardware monitoring (`jtop`), and **Docker Service Manager**.
*   **Main PC (Brain-Cruncher):**
    *   IP Address: 192.168.1.16 (Management Console)
    *   Purpose: Large AI models, resource-intensive tasks, and remote monitoring target.

## Roadmap / To-Do
### Phase 1: Foundational Access & Control
- [x] Configure SSH access to Jetson.
- [x] Implement Ambidextrous Web Monitor (Windows Dashboard + Jetson Host).
- [x] Integrate `jetson-stats` (jtop) for robust hardware monitoring.
- [x] Implement **Docker Service Manager** for one-click container control.
- [ ] Set up Wake-on-LAN (WoL) for Main PC (Hardware accessory pending).
- [ ] Establish secure remote desktop access to Main PC.

### Phase 2: AI Integration
- [x] Deploy a lightweight QWEN model on Jetson via Ollama.
- [x] Implement chat interface in the dashboard.
- [ ] Develop a mechanism for Jetson to offload tasks to Main PC.

### Phase 3: Advanced Features & Refinements
- [x] Implement stable, compact UI with "Restarting" state tracking.
- [ ] Enhance Data Analyzer microservice with historical metrics.
- [ ] Configure Reverse Proxy for secure external access.
- [ ] Automate routine maintenance tasks.

## Milestones

### [v0.1.0] - 2026-02-08
**Stable Dashboard Baseline**
- **Ambidextrous Architecture**: Unified code for Windows (PC) and Linux/Docker (Jetson).
- **Hybrid Network Monitor**: Instant device listing via ARP cache with background "fleshing out" via Nmap and DNS.
- **Hardware Integration**: Real-time Jetson stats (GPU, Temp, Power) via `jtop`.
- **Service Management**: Full Docker container control (List/Restart) with self-restart safety logic.
- **Remote Control**: Soft and Hard reboot capabilities for the Jetson host.

## Security Considerations
*   Firewall rules on all devices.
*   Strong password policies and SSH key management.
*   Consider VPN for external access.
*   Secure storage for credentials (e.g., environment variables, dedicated secret manager).
