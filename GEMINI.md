# Gemini CLI Project Context: Home AI Companion Project

This document provides an overview of the `home_ai_project`, detailing its purpose, architecture, key components, and operational instructions for the Gemini CLI.

## Project Overview

The `home_ai_project` is a home automation and AI companion system designed to leverage both an always-on Jetson device for lightweight tasks and a powerful Main PC for resource-intensive computational needs. The system aims to centralize control and monitoring while maintaining a focus on **simplicity and minimal complexity**.

## Guiding Principles

*   **Simplicity First**: Jetson integration and dashboard features should be implemented as simply as possible. Avoid over-engineering or unnecessary layers of abstraction.
*   **Leverage Open Source**: Use established libraries like `jetson-stats` (jtop) to simplify data collection from NVIDIA hardware, rather than manually parsing system logs or command output.
*   **Low Complexity Dashboard**: The user interface should be clean, functional, and easy to maintain. We can take inspiration from projects like `jetson-stats-grafana-dashboard` for metrics and layout without necessarily adopting their entire stack (e.g., Prometheus/Grafana).
*   **Direct Communication**: Use straightforward HTTP calls and system commands (`subprocess`, `dbus-send`) rather than complex orchestration frameworks where possible.

## Key Hardware & Network Configuration

*   **Jetson (Always-On Companion)**: Targeted for local QWEN models, network management scripts, and Wake-on-LAN initiation. IP: 192.168.1.11.
*   **Main PC (Brain-Cruncher)**: Used for larger AI models, resource-intensive tasks, and as a remote access target.
*   **Network**: SSH access is configured for the Jetson. The system utilizes environment variables (e.g., `MONITOR_TARGET_HOST`, `OLLAMA_HOST`) for inter-component communication and configuration.

## Core Components

### 1. `web_monitor/`

A client-server web application providing real-time monitoring and control. This application is designed to be **ambidextrous**, adapting its functionality based on the host operating system.

*   **PC Dashboard (Windows)**:
    *   Acts as a management console for the local PC.
    *   **Remote Monitoring**: Fetches and displays data from the Jetson by forwarding requests to the Jetson's `web_monitor` instance via the `MONITOR_TARGET_HOST` IP.
    *   **Remote Control**: Sends commands (like reboot) to the Jetson's API.
    *   **Logic**: Does **not** contain direct SSH or host-level control logic (like `dbus-send`). It relies entirely on HTTP communication with the Jetson.
*   **Host Webserver (Jetson/Linux)**:
    *   Acts as the primary data source and control point for the Jetson hardware.
    *   **Data Collection**: Historically used `tegrastats` parsing, but **preferred approach** is to leverage the `jetson-stats` (jtop) Python library for robust and simplified metric collection (inspired by `jetson-stats-grafana-dashboard`).
    *   **System Control**: Executes host-level commands like `dbus-send` for reboots or `docker restart`.
    *   **Internet Access**: Designed to eventually be deployed (e.g., via Docker) and exposed for secure access from the internet.

*   **Technologies**:
    *   **Backend**: Python Flask (`app.py`). Handles API endpoints, system data collection, and serving the React frontend.
    *   **Frontend**: React, built with Vite, using Shadcn UI components and Tailwind CSS.
*   **Architecture & Logic**:
    *   The Flask backend serves the compiled React application from `frontend/dist`.
    *   Differentiates execution environments:
        *   **PC (Windows)**: Does **not** contain Paramiko or direct SSH logic. It makes HTTP calls to the Jetson's `web_monitor` API for remote actions and data.
        *   **Jetson (Ubuntu/Dockerized)**: Executes commands locally on the host via `subprocess` (e.g., `arp -a`, `tegrastats`) or uses `dbus-send` for system reboots. It handles Docker container restarts for soft reboots.
    *   Relies on `MONITOR_TARGET_HOST` environment variable to determine if it should fetch data locally or forward requests to a remote host (Jetson).
*   **Key API Endpoints**:
    *   `/`: Serves the React frontend.
    *   `/api/local_network_status`: Gathers local network device info.
    *   `/api/remote_network_status`: Forwards network status request to `MONITOR_TARGET_HOST`.
    *   `/api/local_system_info`: Gathers local CPU, memory, disk, uptime.
    *   `/api/remote_system_info`: Forwards system info request to `MONITOR_TARGET_HOST`.
    *   `/api/jetson_gpu_info`: Retrieves Jetson GPU stats (`tegrastats`). Forwards from PC to Jetson.
    *   `/api/command/reboot` (POST): Handles soft (Docker restart) and hard (system `dbus-send`) reboots on Jetson, and forwards requests from PC.
    *   `/api/chat` (POST): Interacts with a local Ollama server.
    *   `/api/config`: Provides `MONITOR_TARGET_HOST` status and value to the frontend.

*   **Target Metrics (Inspiration from `jetson-stats-grafana-dashboard`)**:
    *   **Processor**: CPU usage (per-core and total), GPU usage (GR3D), and EMC (memory controller) usage.
    *   **Memory**: RAM usage, Swap usage, and detailed memory frequency.
    *   **Environment**: Temperature (CPU, GPU, Thermal Zones) and Fan speed/mode.
    *   **Power**: Overall power consumption (VDD_IN) and individual rail power (VDD_CPU, VDD_GPU) if available.

*   **Dependencies**: `Flask`, `psutil`, `requests`, `python-dotenv`, `Flask-Cors` (Python). Node.js, npm/yarn for frontend development.
*   **Building & Running**:
    *   **Backend**:
        ```bash
        cd web_monitor
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        python3 app.py
        ```
    *   **Frontend (Development)**:
        ```bash
        cd web_monitor/frontend
        npm install
        npm run dev
        ```
    *   **Frontend (Production Build)**:
        ```bash
        cd web_monitor/frontend
        npm run build
        ```

### 2. `data_analyzer/`

A dedicated microservice for data visualization.

*   **Purpose**: Upload, analyze, and visualize data (currently CSV).
*   **Technologies**: Python Dash, Pandas, Plotly.
*   **Key Features**:
    *   CSV file upload.
    *   Displays DataFrame head and info.
    *   Includes a basic scatter plot placeholder.
*   **Dependencies**: `dash`, `pandas`, `plotly` (Python).
*   **Building & Running**:
    ```bash
    cd data_analyzer
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python3 app.py
    ```

### 3. `scripts/ollama_chat.py`

A utility script for command-line interaction with Ollama.

*   **Purpose**: Send prompts to an Ollama server and receive responses directly from the terminal.
*   **Technologies**: Python, `requests`.
*   **Usage**:
    ```bash
    python scripts/ollama_chat.py "Your prompt here" -m "model_name"
    ```
    (Defaults to `qwen:1.8b` if `-m` is not specified).
*   **Configuration**: Uses `OLLAMA_HOST` environment variable, defaulting to `http://localhost:11434`.
*   **Dependencies**: `requests` (Python).

## General Project Conventions

*   **Virtual Environments**: Python dependencies are managed using virtual environments (`.venv/`) within each component directory.
*   **Configuration**: Environment variables (e.g., via `.env` files) are used for sensitive information and host-specific configurations.
*   **Microservices**: Clear separation of functionalities into independent, deployable services.
*   **Docker Integration**: The presence of `docker-compose.yml` and `Dockerfile` in `web_monitor/` suggests containerized deployment for at least the `web_monitor` application, especially on the Jetson.
