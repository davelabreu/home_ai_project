# Data Gobbler: Modular Analytics Workbench

## Core Vision
A professional-grade, sexy Dash/Plotly application for multi-project data ingestion, visualization, and persistent storage. Designed for engineers to quickly analyze logs and telemetry with total plotting control.

## 🏗️ Architecture (v0.4.0 - Stable)
- **Modular Multi-Page**: Powered by `dash.register_page` for clear separation of concerns.
- **Split-Pane Layout**: Standardized UI with Left Nav, Top Context, and Right Inspector.
- **Data Engine**: Decoupled CSV management (`DataManager`) and signal processing (`Processors`).
- **Global Orchestration**: Centralized `dcc.Store` handles cross-page modal triggers and auto-selection.

## 🚀 Current Roadmap (v0.5.0: The Customization Phase)
- [x] **Split-Pane Layout**: Implemented Top Bar and Right Sidebar (v0.4.0).
- [x] **Plot Card Component**: Reusable unit with contextual gear-trigger.
- [ ] **Trace Inspector**: Implement column renaming and visibility toggles in the slide-out panel.
- [ ] **State Persistence**: Enable saving of inspector changes to a 'Project Plot Template' JSON.
- [ ] **Multi-Plot Canvas**: Enable the '+' FAB to add multiple independent cards dynamically.
- [ ] **Export Engine**: Ability to download processed/cleaned datasets.

## 📜 Coding Bible
Governed by `CODE_RULES.md` and `BACKEND_ARCHITECTURE.md`.