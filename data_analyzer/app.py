import dash
from dash import dcc, html, Input, Output, State, callback_context
import base64
import datetime
import io
import os
import pandas as pd
import plotly.express as px
import json

# Configuration
PROJECTS_ROOT = 'projects'

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# App Layout with Sidebar for Project Selection
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("AI Workbench | Data Analyzer", style={'margin': '0', 'color': 'white'}),
        html.P("Project-based data ingestion and visualization", style={'margin': '0', 'color': '#ccc'})
    ], style={'padding': '20px', 'backgroundColor': '#1e1e1e', 'borderBottom': '2px solid #333'}),

    html.Div([
        # Sidebar
        html.Div([
            html.H4("Projects"),
            dcc.Dropdown(
                id='project-selector',
                options=[
                    {'label': '🏠 Home Jetson Stats', 'value': 'home_jetson'},
                    {'label': '💼 Work Log Analysis', 'value': 'work_logs'},
                ],
                value='home_jetson',
                clearable=False,
                style={'color': 'black'}
            ),
            html.Hr(),
            html.Div(id='project-info', style={'fontSize': '12px', 'color': '#888'})
        ], style={'width': '20%', 'padding': '20px', 'borderRight': '1px solid #ddd', 'height': '100vh', 'float': 'left'}),

        # Main Content Area
        html.Div([
            html.Div(id='project-content')
        ], style={'width': '75%', 'padding': '20px', 'float': 'left'})
    ])
])

# Render Content based on selected project
@app.callback(
    Output('project-content', 'children'),
    Input('project-selector', 'value')
)
def render_project_content(project_id):
    if project_id == 'home_jetson':
        return html.Div([
            html.H2("Home Jetson Stats"),
            html.Button("Fetch Latest from Netdata", id='fetch-netdata-btn', className='btn-primary'),
            html.Div(id='home-stats-display', style={'marginTop': '20px'})
        ])
    else:
        return html.Div([
            html.H2("Work Log Analysis"),
            dcc.Upload(
                id='upload-logs',
                children=html.Div(['Drag and Drop or ', html.A('Select Log/CSV Files')]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'margin': '10px'
                }
            ),
            html.Div(id='log-analysis-display', style={'marginTop': '20px'})
        ])

# --- Logic for Log Ingestion & Persistence ---
@app.callback(
    Output('log-analysis-display', 'children'),
    Input('upload-logs', 'contents'),
    State('upload-logs', 'filename'),
    State('project-selector', 'value')
)
def handle_log_upload(contents, filename, project_id):
    if contents is None:
        # Try to load existing data for the project
        project_dir = os.path.join(PROJECTS_ROOT, project_id)
        files = [f for f in os.listdir(project_dir) if f.endswith('.csv')]
        if files:
            df = pd.read_csv(os.path.join(project_dir, files[0]))
            return render_data_summary(df, f"Restored from {files[0]}")
        return html.P("No data ingested yet for this project.")

    # Process new upload
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    
    # Persist to disk
    save_path = os.path.join(PROJECTS_ROOT, project_id, f"ingested_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(save_path, index=False)
    
    return render_data_summary(df, f"Successfully ingested {filename}")

def render_data_summary(df, message):
    return html.Div([
        html.Div(message, style={'color': 'green', 'fontWeight': 'bold'}),
        html.H5("Data Preview:"),
        html.Div(style={'overflowX': 'auto'}, children=[
            dash.dash_table.DataTable(
                data=df.head(10).to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '5px'},
                style_header={'backgroundColor': '#f4f4f4', 'fontWeight': 'bold'}
            )
        ]),
        dcc.Graph(
            figure=px.line(df, x=df.columns[0], y=df.columns[1:]) if not df.empty else {}
        )
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
