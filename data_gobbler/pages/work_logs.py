import dash
from dash import html, dcc, Input, Output, callback, State, ALL, MATCH
import dash_bootstrap_components as dbc
from utils.data_manager import DataManager
from utils.plotting import PlotTemplates
from components.plot_card import render_plot_card
import pandas as pd
import json

dash.register_page(__name__, path='/work-logs')

def layout():
    projects = DataManager.get_projects()
    log_projects = {pid: info for pid, info in projects.items() if info['type'] in ['logs', 'encoder_analysis']}
    
    return dbc.Container([
        # 0. IDENTIFIER
        dbc.Row([
            dbc.Col([
                dbc.Badge([html.I(className="bi bi-eye-fill me-2"), "LIVE DATA VIEW"], color="success", className="mb-2 p-2 px-3 shadow-sm")
            ], width=12)
        ]),

        # 1. DATA CONTEXT (Hierarchical Navigator)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-sliders2 me-2"), "Data Context"
                    ], className="fw-bold small"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Project", className="small fw-bold mb-1"),
                                dcc.Dropdown(
                                    id='log-project-selector',
                                    options=[{'label': p['name'], 'value': pid} for pid, p in log_projects.items()],
                                    value=list(log_projects.keys())[0] if log_projects else None,
                                    clearable=False,
                                    style={'color': 'black'}
                                ),
                            ], width=3),
                            dbc.Col([
                                html.Label("Subsystem", className="small fw-bold mb-1"),
                                dcc.Dropdown(
                                    id='log-subsystem-selector', 
                                    placeholder="Select...",
                                    style={'color': 'black'}
                                ),
                            ], width=3),
                            dbc.Col([
                                html.Label("Test / Session", className="small fw-bold mb-1"),
                                dcc.Dropdown(
                                    id='log-test-selector', 
                                    placeholder="Select...",
                                    style={'color': 'black'}
                                ),
                            ], width=3),
                            dbc.Col([
                                html.Label("Data File", className="small fw-bold mb-1"),
                                dcc.Dropdown(
                                    id='log-file-selector', 
                                    placeholder="Select...",
                                    style={'color': 'black'}
                                ),
                            ], width=3),
                        ])
                    ])
                ], className="mb-4 shadow-sm border-0", style={"background-color": "#1e1e1e"})
            ], width=12)
        ]),

        # 2. CENTRAL CANVAS (The Grid of Plot Cards)
        dbc.Row([
            dbc.Col([
                html.Div(id="plot-canvas", children=[
                    render_plot_card("main-plot", title="Analysis Canvas")
                ])
            ], width=12)
        ]),

        # 3. GLOBAL METADATA / STATS BAR
        dbc.Row([
            dbc.Col(html.Div(id="log-file-metadata", className="small text-muted mb-4"), width=12)
        ]),

        # 4. ADD PLOT BUTTON (FAB)
        html.Div([
            dbc.Button(
                html.I(className="bi bi-plus-lg"),
                id="add-plot-btn",
                color="success",
                className="rounded-circle shadow-lg",
                style={"width": "60px", "height": "60px", "font-size": "24px"}
            )
        ], style={"position": "fixed", "bottom": "2rem", "right": "2rem", "z-index": "100"})

    ], fluid=True)

# --- Callbacks for Hierarchical Selection ---

@callback(
    [Output('log-project-selector', 'value'),
     Output('log-subsystem-selector', 'value'),
     Output('log-test-selector', 'value'),
     Output('log-file-selector', 'value')],
    Input('last-ingested-file', 'data'),
    prevent_initial_call=True
)
def auto_select_full_context(last_ingest):
    if last_ingest and 'project_id' in last_ingest:
        return (
            last_ingest['project_id'],
            last_ingest.get('subsystem', 'general'),
            last_ingest.get('test', 'quick_dump'),
            last_ingest['filename']
        )
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@callback(
    Output('log-subsystem-selector', 'options'),
    Input('log-project-selector', 'value')
)
def update_subsystems(project_id):
    if not project_id: return []
    subs = DataManager.list_subsystems(project_id)
    return [{'label': s, 'value': s} for s in subs]

@callback(
    Output('log-test-selector', 'options'),
    [Input('log-project-selector', 'value'),
     Input('log-subsystem-selector', 'value')]
)
def update_tests(project_id, subsystem):
    if not project_id or not subsystem: return []
    tests = DataManager.list_tests(project_id, subsystem)
    return [{'label': t, 'value': t} for t in tests]

@callback(
    Output('log-file-selector', 'options'),
    [Input('log-project-selector', 'value'),
     Input('log-subsystem-selector', 'value'),
     Input('log-test-selector', 'value')]
)
def update_files(project_id, subsystem, test):
    if not project_id or not subsystem or not test: return []
    files = DataManager.list_files(project_id, subsystem, test)
    return [{'label': f, 'value': f} for f in files]

# Callback 1: Update Metadata
@callback(
    Output('log-file-metadata', 'children'),
    [Input('log-file-selector', 'value')],
    [State('log-project-selector', 'value'),
     State('log-subsystem-selector', 'value'),
     State('log-test-selector', 'value')]
)
def update_metadata(filename, project_id, subsystem, test):
    if not filename: return ""
    df = DataManager.load_dataframe(project_id, subsystem, test, filename)
    return f"Loaded: {subsystem} / {test} / {filename} | Records: {len(df)} | Columns: {len(df.columns)}"

# Callback 2: Update Individual Plots
@callback(
    Output({'type': 'plot-graph', 'index': MATCH}, 'figure'),
    [Input('log-file-selector', 'value')],
    [State('log-project-selector', 'value'),
     State('log-subsystem-selector', 'value'),
     State('log-test-selector', 'value'),
     State({'type': 'plot-graph', 'index': MATCH}, 'id')]
)
def update_plots(filename, project_id, subsystem, test, plot_id_obj):
    if not filename: return dash.no_update
    
    df = DataManager.load_dataframe(project_id, subsystem, test, filename)
    projects = DataManager.get_projects()
    template = projects[project_id].get('template')
    
    if template == 'encoder_quadrature':
        fig = PlotTemplates.encoder_analysis_v6(df, title=f"Encoder Analysis")
    else:
        import plotly.express as px
        fig = px.line(df, x=df.columns[0], y=df.columns[1:], title="Generic Analysis", template="plotly")
    
    return fig
