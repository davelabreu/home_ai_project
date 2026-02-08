# Data Gobbler: Modular Analytics Workbench

## Core Vision
A professional-grade, sexy Dash/Plotly application for multi-project data ingestion, visualization, and persistent storage. Designed for engineers to quickly analyze logs and telemetry with total plotting control.

## 🏗️ Architecture (v0.4.1 - Stable)
- **Hierarchical Storage**: Subsystem/Test level organization for complex engineering data.
- **Split-Pane Layout**: Standardized UI with Left Nav, Top Context, Central Canvas, Right Inspector.
- **Deep Linking**: Ability to auto-navigate to specific nested files after ingestion.

## 🚀 Current Roadmap (v0.5.0: The Customization Phase)
- [x] **Split-Pane Layout**: Implemented Top Bar and Right Sidebar.
- [x] **Hierarchical Context**: Added Subsystem -> Test -> File navigation.
- [x] **Deep Auto-Selection**: Solved dropdown race conditions for instant view.
- [ ] **Trace Inspector**: Implement column renaming and visibility toggles in the slide-out panel.
- [ ] **State Persistence**: Enable saving of inspector changes to a 'Project Plot Template' JSON.
- [ ] **Multi-Plot Canvas**: Enable the '+' FAB to add multiple independent cards dynamically.

## 📜 Coding Bible
Governed by `CODE_RULES.md` and `BACKEND_ARCHITECTURE.md`.