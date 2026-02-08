# Data Analyzer: AI Workbench Context

## 🚀 Status: External Development (v0.2.2 Stable)
**Active development of the AI Workbench core has transitioned to a standalone repository.** This directory now serves as the **Production Deployment** target for the Jetson.

## Core Vision
A "Low-Code Analytics Platform" for multi-project data ingestion, visualization, and persistent storage. 
*   **LLM Integration (Future)**: Leverage Jetson-hosted lightweight models (Ollama) to automate data parsing, cleaning, and organizational logic prior to plotting.

## 🏗️ Strict Architectural Guardrails (Safeguarding Jetson Integration)

### 1. The "Hidden DOM" Rule
**Constraint**: Dash callbacks will crash if an `Input` ID is missing from the layout.
**Implementation**: All project-specific controls must be declared in the main `app.layout` at boot. 
**Expansion**: Maintain this pattern in current production to avoid breaking the Jetson dashboard during maintenance.

### 2. Networking & Host Binding
**Jetson Accessibility**: Always bind to `0.0.0.0:8050` inside the container.
**Internal Proxy**: When fetching Netdata stats, use the internal Docker DNS `http://netdata:19999`.

### 3. Persistence (Data Integrity)
**Volume Mapping**: Data is persisted via Docker volumes to `projects/`. Ensure any external V2 build maintains the `projects/[project_id]/[type]_[timestamp].csv` directory structure to allow for seamless data migration.

## Current State (v0.2.2)
- **Stable Base**: Project Registry, Sidebar Library, and Netdata Fetcher are fully functional.
- **Maintenance Mode**: Only critical bug fixes or security patches should be applied to this directory.

## External V2 Roadmap (Standalone Repo)
- [ ] **Modular Architecture**: Transition to Dash Pages.
- [ ] **Styling**: Implement Dash Bootstrap Components (DBC) with Darkly theme.
- [ ] **Data Controller**: Decouple Pandas logic from UI callbacks.
- [ ] **AI Orchestrator**: Interface with Jetson Ollama API for data pre-processing.
