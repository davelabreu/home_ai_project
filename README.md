# Home AI Companion Project

This `README.md` provides a high-level overview of the entire `home_ai_project`. For details on specific components, please refer to their respective README files.

## Project Structure

*   `README.md`: This file, providing a high-level overview of the project, vision, hardware, network, roadmap, and security considerations.
*   `scripts/`: Contains various utility scripts for system management, automation, and AI model interactions.
*   `web_monitor/`: The main web application for monitoring and managing the Jetson device and other home AI components. It consists of a Flask backend and a React frontend.
*   `data_analyzer/`: A Dash Plotly application for ingesting, analyzing, and visualizing data, designed to run as a separate microservice.

## Vision
To create a robust home automation and AI companion system, leveraging a Jetson device for always-on lightweight tasks and a powerful main PC for intensive computational needs (e.g., advanced AI models). The system aims to centralize control, enhance remote accessibility, and manage home network resources efficiently.

## Hardware Components
*   **Jetson (Always-On Companion):**
    *   Hostname: [e.g., jetson-nano]
    *   IP Address: 192.168.1.11
    *   Purpose: Local QWEN model, home network management scripts, Wake-on-LAN initiator.
*   **Main PC (Brain-Cruncher):**
    *   Hostname: [e.g., gaming-pc]
    *   IP Address: [e.g., 192.168.1.10]
    *   MAC Address: [e.g., AA:BB:CC:DD:EE:FF]
    *   GPU: 5060ti
    *   Purpose: Running larger AI models, resource-intensive tasks, remote access target.

## Network Configuration
| Device      | IP Address    | MAC Address         | Notes                                      |
| :---------- | :------------ | :------------------ | :----------------------------------------- |
| Jetson      | 192.168.1.11  | [Jetson MAC]        | SSH access configured (ssh jetson)         |
| Main PC     | [Main PC IP]  | [Main PC MAC]       | Target for Wake-on-LAN and remote access   |
| ...         | ...           | ...                 | (Add other relevant devices)               |

## Roadmap / To-Do
### Phase 1: Foundational Access & Control
- [x] Configure SSH access to Jetson (using `ssh jetson`).
- [ ] Set up Wake-on-LAN (WoL) for Main PC, initiated from Jetson.
- [ ] Establish secure remote desktop access (e.g., VNC, RDP, NoMachine) to Main PC.
- [ ] Document network structure and IP allocations.
- [x] Implement basic scripts for network monitoring/management on Jetson.

### Phase 2: AI Integration
- [x] Deploy a lightweight QWEN model on Jetson for daily tasks.
- [ ] Develop a mechanism for Jetson to offload tasks to Main PC.
- [ ] Implement secure API access for models on Main PC.

### Phase 3: Advanced Features & Refinements
- [ ] Implement robust logging and monitoring for all components.
- [ ] Enhance security protocols (VPN, firewall rules).
- [ ] Develop a user-friendly interface for overall system management.
- [ ] Automate routine tasks and maintenance.

## Security Considerations
*   Firewall rules on all devices.
*   Strong password policies and SSH key management.
*   Consider VPN for external access.
*   Secure storage for credentials (e.g., environment variables, dedicated secret manager).
