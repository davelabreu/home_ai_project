# Data Gobbler: Backend Architecture & Data Flow

This document explains the "Engine Room" of the engineering workbench.

## 🔄 1. The Ingestion Lifecycle
When a user uploads a file via the **Ingest Wizard**, the following happens:
1.  **Transport**: The CSV is encoded as a base64 string and sent to the server.
2.  **Contextual Routing**: The wizard checks `projects.json` to find the project's **Template**.
3.  **Transformation**: If a template exists (e.g., `encoder_quadrature`), the `utils/processors.py` engine runs the specific Pandas logic (decoding A/B phases, calculating velocity).
4.  **Silo Storage**: The `DataManager` saves the result to `projects/[project_id]/ingest_YYYY-MM-DD_HH-MM.csv`.
5.  **Signal Propagation**: A success record is saved to `last-ingested-file` (dcc.Store), which triggers the UI to redirect and auto-select.

## 🏗️ 2. Modular Component Registry
Instead of one giant file, the UI is built from isolated modules:
*   **`DataManager` (`utils/data_manager.py`)**: The primary interface for the filesystem. Handles all `glob`, `mkdir`, and `read_csv` operations.
*   **`PlotTemplates` (`utils/plotting.py`)**: A library of "High-Value" Plotly recipes. It takes a DataFrame and returns a complex `go.Figure`.
*   **`PlotCard` (`components/plot_card.py`)**: A UI wrapper that provides the "Gear" icon and handles pattern-matching IDs (`MATCH`).
*   **`Inspector` (`components/inspector_panel.py`)**: A contextual sidebar that listens for "Gear" clicks and populates based on the active plot's columns.

## 🧠 3. Advanced Callback Patterns
To maintain stability, we follow these two critical patterns:

### The "Hidden DOM" Rule
We never conditionally render components that contain `Input` IDs. Instead, we render everything at boot and use `style={'display': 'none'}` to toggle visibility. This ensures Dash never crashes with a "Nonexistent object" error.

### The "initial_duplicate" Rule
When multiple callbacks target the same output (like the file selector), we use `allow_duplicate=True`. To prevent conflicts on page load, the secondary callback must set `prevent_initial_call='initial_duplicate'`.

## 📁 4. Persistence Directory Structure
```text
data_gobbler/
├── projects/
│   ├── home_jetson/      # Siloed CSVs
│   └── encoder_analysis/ # Processed Quadrature data
├── projects.json         # Project Registry (Metadata)
└── templates/            # (Future) Saved JSON plot configurations
```
