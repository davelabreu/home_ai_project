import dash
from dash import html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
from utils.data_manager import DataManager
from utils.plotting import PlotTemplates
import pandas as pd

dash.register_page(__name__, path='/work-logs')

def layout():
    # Load all log projects
    projects = DataManager.get_projects()
    log_projects = {pid: info for pid, info in projects.items() if info['type'] in ['logs', 'encoder_analysis']}
    
    return dbc.Container([
        dbc.Row([
            # Left Column: Project & File Selection
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Project Navigator"),
                    dbc.CardBody([
                        html.Label("Select Project:"),
                        dcc.Dropdown(
                            id='log-project-selector',
                            options=[{'label': p['name'], 'value': pid} for pid, p in log_projects.items()],
                            value=list(log_projects.keys())[0] if log_projects else None,
                            clearable=False,
                            className="mb-3",
                            style={'color': 'black'}
                        ),
                        html.Label("Select File:"),
                        dcc.Dropdown(
                            id='log-file-selector', 
                            placeholder="Select a file...",
                            style={'color': 'black'}
                        ),
                    ])
                ], className="mb-4 shadow-sm"),
                
                dbc.Card([
                    dbc.CardHeader("Quick Info"),
                    dbc.CardBody(id="log-file-metadata", className="small text-muted")
                ], className="shadow-sm")
            ], width=3),

            # Right Column: Main Visualization Area
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-main-plot",
                            type="default",
                            children=dcc.Graph(id="log-main-plot", style={'height': '80vh'})
                        )
                    ])
                ], className="shadow-lg")
            ], width=9)
        ])
    ], fluid=True, className="mt-2")

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

@callback(
    [Output('log-main-plot', 'figure'),
     Output('log-file-metadata', 'children')],
    [Input('log-file-selector', 'value')],
    [State('log-project-selector', 'value')]
)
def update_main_viz(filename, project_id):
    if not filename or not project_id:
        return {}, "Select a file to view stats."
    
    # 1. Load Data
    df = DataManager.load_dataframe(project_id, filename)
    
    # 2. Identify Project Type & Template
    projects = DataManager.get_projects()
    template = projects[project_id].get('template')
    
    # 3. Generate Figure
    if template == 'encoder_quadrature':
        fig = PlotTemplates.encoder_analysis_v6(df, title=f"Encoder Analysis: {filename}")
    else:
        # Default fallback plot
        import plotly.express as px
        fig = px.line(df, x=df.columns[0], y=df.columns[1:], title=f"Generic Log: {filename}", template="plotly")
    
    # 4. Generate Metadata
    metadata = [
        html.P(f"Filename: {filename}"),
        html.P(f"Rows: {len(df)}"),
        html.P(f"Columns: {len(df.columns)}")
    ]
    
    return fig, metadata
