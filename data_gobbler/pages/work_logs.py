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
        # 1. TOP BAR (Global Controls)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Active Project", className="small fw-bold mb-1"),
                                dcc.Dropdown(
                                    id='log-project-selector',
                                    options=[{'label': p['name'], 'value': pid} for pid, p in log_projects.items()],
                                    value=list(log_projects.keys())[0] if log_projects else None,
                                    clearable=False,
                                    style={'color': 'black'}
                                ),
                            ], width=4),
                            dbc.Col([
                                html.Label("Data File", className="small fw-bold mb-1"),
                                dcc.Dropdown(
                                    id='log-file-selector', 
                                    placeholder="Select a file...",
                                    style={'color': 'black'}
                                ),
                            ], width=4),
                            dbc.Col([
                                html.Div(id="log-file-metadata", className="mt-4 small text-muted text-end")
                            ], width=4)
                        ])
                    ])
                ], className="mb-4 shadow-sm border-0", style={"background-color": "#1e1e1e"})
            ], width=12)
        ]),

        # 2. CENTRAL CANVAS (The Grid of Plot Cards)
        dbc.Row([
            dbc.Col([
                html.Div(id="plot-canvas", children=[
                    # We'll start with one default plot card
                    render_plot_card("main-plot", title="Initial Analysis View")
                ])
            ], width=12)
        ]),

        # 3. ADD PLOT BUTTON (FAB)
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

# --- Callbacks ---

@callback(
    Output('log-file-selector', 'options'),
    Input('log-project-selector', 'value')
)
def update_file_dropdown(project_id):
    if not project_id:
        return []
    files = DataManager.list_files(project_id)
    return [{'label': f, 'value': f} for f in files]

# Callback 1: Update Metadata (Static ID)
@callback(
    Output('log-file-metadata', 'children'),
    [Input('log-file-selector', 'value')],
    [State('log-project-selector', 'value')]
)
def update_metadata(filename, project_id):
    if not filename or not project_id:
        return "No file selected."
    df = DataManager.load_dataframe(project_id, filename)
    return f"Records: {len(df)} | Cols: {len(df.columns)}"

# Callback 2: Update Individual Plots (MATCH Wildcard)
@callback(
    Output({'type': 'plot-graph', 'index': MATCH}, 'figure'),
    [Input('log-file-selector', 'value')],
    [State('log-project-selector', 'value'),
     State({'type': 'plot-graph', 'index': MATCH}, 'id')]
)
def update_plots(filename, project_id, plot_id_obj):
    if not filename or not project_id:
        return dash.no_update
    
    df = DataManager.load_dataframe(project_id, filename)
    projects = DataManager.get_projects()
    template = projects[project_id].get('template')
    
    # Logic for individual cards
    if template == 'encoder_quadrature':
        fig = PlotTemplates.encoder_analysis_v6(df, title=f"Encoder Analysis")
    else:
        import plotly.express as px
        fig = px.line(df, x=df.columns[0], y=df.columns[1:], title="Generic Line Plot", template="plotly")
    
    return fig