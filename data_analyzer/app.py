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
# Load project registry
def load_projects():
    with open('projects.json', 'r') as f:
        return json.load(f)

PROJECTS = load_projects()

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("AI Workbench | Data Analyzer", style={'margin': '0', 'color': 'white'}),
        html.P("v0.2.0 - Project-based Analytics Workbench", style={'margin': '0', 'color': '#ccc'})
    ], style={'padding': '20px', 'backgroundColor': '#1e1e1e', 'borderBottom': '2px solid #333'}),

    html.Div([
        # Sidebar
        html.Div([
            html.H4("Project Navigator"),
            dcc.Dropdown(
                id='project-selector',
                options=[{'label': info['name'], 'value': pid} for pid, info in PROJECTS.items()],
                value='home_jetson',
                clearable=False,
                style={'color': 'black'}
            ),
            html.Hr(),
            html.Div(id='project-metadata', style={'fontSize': '13px', 'color': '#555', 'marginBottom': '20px'}),
            html.H5("Data Library"),
            html.Div(id='data-library-list', style={'fontSize': '12px'})
        ], style={'width': '20%', 'padding': '20px', 'borderRight': '1px solid #ddd', 'minHeight': '100vh', 'float': 'left', 'backgroundColor': '#f9f9f9'}),

        # Main Content
        html.Div([
            html.Div(id='project-content')
        ], style={'width': '75%', 'padding': '20px', 'float': 'left'})
    ])
])

# Sidebar: Update Metadata and Library List
@app.callback(
    [Output('project-metadata', 'children'),
     Output('data-library-list', 'children')],
    [Input('project-selector', 'value'),
     Input('home-stats-display', 'children'), # Refresh when new data fetched
     Input('log-analysis-display', 'children')] # Refresh when new log uploaded
)
def update_sidebar(project_id, _n1, _n2):
    project = PROJECTS[project_id]
    metadata = html.Div([
        html.P(project['description']),
        html.Code(f"Template: {project['template']}", style={'fontSize': '10px'})
    ])
    
    project_dir = ensure_project_dir(project_id)
    files = sorted([f for f in os.listdir(project_dir) if f.endswith('.csv')], reverse=True)
    
    if not files:
        library = html.P("No files found.", style={'fontStyle': 'italic'})
    else:
        library = html.Ul([
            html.Li(f, style={'cursor': 'pointer', 'color': '#0066cc', 'marginBottom': '5px'}) 
            for f in files[:10] # Show last 10
        ], style={'paddingLeft': '15px'})
        
    return metadata, library

# Main Content: Render based on Project
@app.callback(
    Output('project-content', 'children'),
    Input('project-selector', 'value')
)
def render_project_content(project_id):
    project = PROJECTS[project_id]
    if project_id == 'home_jetson':
        return html.Div([
            html.H2(project['name']),
            html.Button("Fetch Latest from Netdata", id='fetch-netdata-btn', className='btn-primary', style={'padding': '10px 20px', 'backgroundColor': '#007bff', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
            html.Div(id='home-stats-display', style={'marginTop': '20px'})
        ])
    else:
        return html.Div([
            html.H2(project['name']),
            dcc.Upload(
                id='upload-logs',
                children=html.Div(['Drag and Drop or ', html.A('Select Log/CSV Files')]),
                style={
                    'width': '100%', 'height': '80px', 'lineHeight': '80px',
                    'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '10px',
                    'textAlign': 'center', 'backgroundColor': '#f8f9fa'
                }
            ),
            html.Div(id='log-analysis-display', style={'marginTop': '20px'})
        ])

import requests # Import requests for Netdata API

# --- Helper to ensure directories exist ---
def ensure_project_dir(project_id):
    path = os.path.join(PROJECTS_ROOT, project_id)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

# Callback to handle BOTH Netdata Fetch and File Upload
@app.callback(
    Output('home-stats-display', 'children'),
    Input('fetch-netdata-btn', 'n_clicks'),
    prevent_initial_call=True
)
def fetch_netdata_stats(n_clicks):
    if not n_clicks:
        return ""
    
    try:
        # High-value Jetson Metrics
        # Mapping Netdata chart names to friendly labels
        chart_map = {
            'system.cpu': 'CPU %',
            'mem.available': 'Available RAM',
            'system.load': 'Sys Load',
            'system.uptime': 'Uptime',
            'cpu.cpufreq': 'CPU Freq (MHz)',
            'sensors.voltage_ina3221-i2c-1-40_in2_VDD_CPU_GPU_CV_input': 'CPU/GPU Power (mW)'
        }
        
        all_data = []
        for chart_id, label in chart_map.items():
            try:
                url = f"http://netdata:19999/api/v1/data?chart={chart_id}&after=-3600&format=json"
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    res_json = response.json()
                    cols = ['time'] + [f"{label} ({l})" for l in res_json['labels'][1:]]
                    chart_df = pd.DataFrame(res_json['data'], columns=cols)
                    chart_df['time'] = pd.to_datetime(chart_df['time'], unit='s')
                    all_data.append(chart_df.set_index('time'))
            except:
                continue # Skip if a specific sensor is missing

        if not all_data:
            return html.Div("Could not fetch any data from Netdata. Are the sensors active?", style={'color': 'orange'})

        # Merge all charts into one master DataFrame
        df = pd.concat(all_data, axis=1).sort_index().reset_index()
        
        # Persist to disk
        project_dir = ensure_project_dir('home_jetson')
        save_path = os.path.join(project_dir, f"jetson_stats_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(save_path, index=False)
        
        return render_data_summary(df, f"Fetched {len(df)} records (Uptime, Power, CPU, RAM)")
    except Exception as e:
        return html.Div(f"Error fetching from Netdata: {str(e)}", style={'color': 'red'})

# Fixed handle_log_upload with directory safety
@app.callback(
    Output('log-analysis-display', 'children'),
    Input('upload-logs', 'contents'),
    State('upload-logs', 'filename'),
    State('project-selector', 'value')
)
def handle_log_upload(contents, filename, project_id):
    project_dir = ensure_project_dir(project_id)
    
    if contents is None:
        files = sorted([f for f in os.listdir(project_dir) if f.endswith('.csv')], reverse=True)
        if files:
            df = pd.read_csv(os.path.join(project_dir, files[0]))
            return render_data_summary(df, f"Restored latest data: {files[0]}")
        return html.P("No data ingested yet for this project.")

    # Process new upload
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    
    # Safety: ensure dir exists before pandas tries to write
    save_path = os.path.join(project_dir, f"ingested_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
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
