# Data Analyzer Sub-Project Context

This document manages the evolution of the `data_analyzer` component, which has evolved from a simple CSV viewer into the **AI Workbench**.

## Core Vision
A "Low-Code Analytics Platform" for multi-project data ingestion, visualization, and persistent storage. It allows the user to manage professional logs and home telemetry in a unified interface.

## Architecture: The "Workbench" Pattern
1.  **Project-Based**: All data is siloed by Project ID (e.g., `home_jetson`, `work_logs`).
2.  **Configuration as Code**: Projects are defined in `projects.json`.
3.  **Persistence**: Data is saved as CSV files in `projects/[project_id]/` and persists via Docker volume mounts.
4.  **Template Engine (Future)**: Specific visualization templates mapped to project types.

## Current State (v0.2.0)
- **Project Registry**: Dynamic project loading via JSON.
- **Data Library**: Automatic scanning and listing of ingested files in the sidebar.
- **Jetson Fetcher**: Built-in logic to pull real-time hardware metrics (Power, CPU, Freq) from Netdata.
- **Persistent Ingestion**: Standardized file upload with auto-saving to project directories.

## Roadmap
- [ ] **Data Selection**: Enable clicking items in the 'Data Library' to reload historical views.
- [ ] **Custom Templates**: Implement specific visual layouts for `hardware_telemetry` vs `log_generic`.
- [ ] **Memory Persistence**: Implement `dcc.Store` for faster session switching.
- [ ] **Export Engine**: Ability to clean and re-export merged datasets.
