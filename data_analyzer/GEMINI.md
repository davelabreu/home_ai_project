# Data Analyzer: AI Workbench Context

## Core Vision
A "Low-Code Analytics Platform" for multi-project data ingestion, visualization, and persistent storage.

## 🏗️ Strict Architectural Guardrails (DO NOT BREAK)

### 1. The "Hidden DOM" Rule
**Constraint**: Dash callbacks will crash if an `Input` ID is missing from the layout.
**Implementation**: All project-specific controls (e.g., `upload-logs`, `fetch-netdata-btn`) must be declared in the main `app.layout` at boot. 
**Expansion**: To add a new project type, add its controls to `app.layout` and use the `toggle_controls` callback to manage visibility via CSS `display: block/none`. **Never** use conditional rendering (returning different components from a callback) for Input objects.

### 2. Project-Based Silos
**Registry**: `projects.json` is the single source of truth for project metadata.
**Storage**: Data MUST be stored in `projects/[project_id]/`. 
**Naming**: Ingested files should follow `[type]_[timestamp].csv` format for easy sorting.

### 3. The "Shared Display" Pattern
**Consistency**: All visualizations and data previews MUST render into the `shared-display-area`.
**State**: Use the `data-update-signal` (dcc.Store) to notify the sidebar/library that the filesystem has changed.

## Current State (v0.2.2 - Stable)
- **Navigator**: Sidebar with Project Registry and Data Library.
- **Persistence**: Host-backed CSV storage via Docker volumes.
- **Stability**: Resolved all callback dependency errors via the Hidden DOM pattern.

## Roadmap
- [ ] **Template Engine**: Map `project['template']` to specific Plotly configurations.
- [ ] **Data Cleanup**: Add a "Delete" button to items in the Data Library.
- [ ] **Sub-filtering**: Ability to filter the active DataFrame by column values.