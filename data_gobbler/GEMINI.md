# Data Gobbler: Modular Analytics Workbench

## Core Vision
A professional-grade, sexy Dash/Plotly application for multi-project data ingestion, visualization, and persistent storage. Designed for engineers to quickly analyze logs and telemetry with total plotting control.

## Lofty Goals (The "Master Plan")
1.  **Project-Based Ingestion**: Unified entry point for any CSV, routed to project-specific silos.
2.  **Persistent Data Library**: Store and manage uploaded logs for later recall.
3.  **Pro Plotting Engine**: Total control over trace colors, thickness, types, and multi-plot layouts.
4.  **Saveable Templates**: Save custom plotting configurations as JSON templates to reuse across different datasets.
5.  **LLM Ingestion (Future)**: Integrate Jetson-hosted LLMs to help parse complex logs and suggest visualizations.

## Architecture (v0.3.1)
- **Framework**: Dash 2.5+ (Multi-page via `pages/`).
- **UI**: Dash Bootstrap Components (DBC) with `DARKLY` theme and custom CSS fixes.
- **Rules**: Governed by `CODE_RULES.md`.
- **Navigation**: Persistent Navbar with global Ingestion Wizard and project-based routing.

## Current Roadmap (v0.4.0: The Canvas & Inspector Phase)
- [x] **Scaffold Architecture**: Modular Pages structure and requirements.
- [x] **Data Manager Engine**: Robust CSV handling and project siloing logic.
- [x] **Ingestion Wizard**: Multi-step modal for file routing and pre-processing.
- [ ] **Split-Pane Layout**: Implement Top Bar (Global Controls) and Right Sidebar (Contextual Inspector).
- [ ] **Plot Card Component**: Reusable card with settings trigger for independent plotting.
- [ ] **No-Code Customization**: Header renaming and trace toggling via Inspector UI.
- [ ] **Template Engine**: Saveable plotting configurations (JSON).
