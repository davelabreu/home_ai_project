# Data Gobbler: Modular Analytics Workbench

## Core Vision
A professional-grade, sexy Dash/Plotly application for multi-project data ingestion, visualization, and persistent storage. Designed for engineers to quickly analyze logs and telemetry with total plotting control.

## Lofty Goals (The "Master Plan")
1.  **Project-Based Ingestion**: Unified entry point for any CSV, routed to project-specific silos.
2.  **Persistent Data Library**: Store and manage uploaded logs for later recall.
3.  **Pro Plotting Engine**: Total control over trace colors, thickness, types, and multi-plot layouts.
4.  **Saveable Templates**: Save custom plotting configurations as JSON templates to reuse across different datasets.
5.  **LLM Ingestion (Future)**: Integrate Jetson-hosted LLMs to help parse complex logs and suggest visualizations.

## Architecture (v0.3.0)
- **Framework**: Dash 2.5+ (Multi-page via `pages/`).
- **UI**: Dash Bootstrap Components (DBC) with `DARKLY` theme.
- **Rules**: Governed by `CODE_RULES.md`.
- **Target Host**: Standalone development on PC -> Final deployment on Jetson.

## Current Roadmap
- [x] **Scaffold Architecture**: Modular Pages structure, requirements, and Docker integration.
- [ ] **Data Manager Utility**: Build the `utils/data_manager.py` to handle CSV loading and project folder management.
- [ ] **Unified Ingestion Page**: Create an 'Upload' page that handles CSV ingestion and project assignment.
- [ ] **Template Engine Foundation**: Start defining how a 'Plot Template' JSON looks.
