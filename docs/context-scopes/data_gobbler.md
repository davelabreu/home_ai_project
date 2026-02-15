# Context Scope: data_gobbler

> Load this file when working on the engineering workbench.

## Service Identity
- **Status**: Active Development (v0.4.1 Stable)
- **Container**: `data_gobbler`
- **Ports**: Host 8052 → Container 8050
- **Stack**: Dash + Dash Bootstrap Components (DARKLY theme) + Plotly + Pandas

## Architecture Summary
- Multi-page Dash app using `dash.page_registry`
- Split-pane UI: Fixed Left Sidebar (nav), Top Bar (context), Central Canvas (plots), Right Inspector (settings)
- Data stored as CSV in hierarchical filesystem, NOT a database
- All dynamic UI components pre-rendered at boot, toggled with CSS (Hidden DOM Rule)

## Key Files
```
data_gobbler/
├── app.py                          # Dash app entry, sidebar, global stores
├── projects.json                   # Project registry (metadata)
├── projects/                       # Data storage root (Docker volume mounted)
│   ├── home_jetson/
│   ├── work_logs/
│   └── encoder_analysis/
├── pages/
│   ├── home.py                     # Landing page
│   ├── work_logs.py                # Main analysis page (hierarchical selectors + plot canvas)
│   └── jetson_stats.py             # Placeholder
├── components/
│   ├── ingest_wizard.py            # Upload modal with project/subsystem/test context
│   ├── plot_card.py                # Individual plot card with settings button
│   └── inspector_panel.py          # Right sidebar for plot settings (Offcanvas)
└── utils/
    ├── data_manager.py             # ALL filesystem operations (list, save, load)
    ├── plotting.py                 # Plotly figure templates (encoder_analysis_v6, etc.)
    └── processors.py               # Data transformation (encoder quadrature decoding)
```

## Critical Patterns

### Hidden DOM Rule
**NEVER** conditionally render components that contain `Input` IDs. Dash will crash.
```python
# WRONG — will crash if component isn't rendered
if show_chart:
    return dcc.Graph(id='my-graph')

# RIGHT — always render, toggle visibility
html.Div(id='chart-container', children=[dcc.Graph(id='my-graph')],
         style={'display': 'block' if show_chart else 'none'})
```

### Deep Auto-Selection (Race Condition Fix)
After ingestion, the `auto_select_full_context` callback returns BOTH `value` AND `options` for every dropdown simultaneously. This prevents dropdowns from rejecting values because options haven't loaded yet.

### Pattern Matching Callbacks
Plot cards use `{'type': 'plot-graph', 'index': MATCH}` for dynamic component targeting.

## Data Flow
```
Upload CSV → Ingest Wizard → (Optional: Processor) → DataManager.save_dataframe()
                                                              ↓
                                                    projects/[pid]/[sub]/[test]/ingest_*.csv
                                                              ↓
                                                    last-ingested-file (dcc.Store, session)
                                                              ↓
                                                    Redirect to /work-logs + auto_select_full_context
```

## Project Registry (projects.json)
| ID | Template | Type |
|---|---|---|
| home_jetson | hardware_telemetry | telemetry |
| work_logs | log_generic | logs |
| encoder_analysis | encoder_quadrature | encoder_analysis |

## Build & Test
```bash
# Local dev
cd data_gobbler && python3 app.py

# Docker rebuild
docker compose up -d --build data_gobbler

# Check at http://192.168.1.11:8052
```

## Roadmap (Next)
- [ ] Trace Inspector: column renaming and visibility toggles in Offcanvas
- [ ] State Persistence: save inspector changes to Project Plot Template JSON
- [ ] Multi-Plot Canvas: FAB button to add independent plot cards dynamically
