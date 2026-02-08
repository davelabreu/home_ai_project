import dash
from dash import dcc, html, Input, Output, State, callback_context
import base64
import datetime
import io
import os
import pandas as pd
import plotly.express as px
import json
import requests

# Configuration
PROJECTS_ROOT = 'projects'

def load_projects():
    with open('projects.json', 'r') as f:
        return json.load(f)

PROJECTS = load_projects()

def ensure_project_dir(project_id):
    path = os.path.join(PROJECTS_ROOT, project_id)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Store(id='data-update-signal', data=0),
    
    # Header
    html.Div([
        html.H1("AI Workbench | Data Analyzer", style={'margin': '0', 'color': 'white'}),
        html.P("v0.2.2 - Project-based Analytics Workbench", style={'margin': '0', 'color': '#ccc'})
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

        # Main Content Area
        html.Div([
            # --- PERSISTENT CONTROLS (Always in DOM to avoid Dash errors) ---
            # Home Jetson Controls
            html.Div(id='ctrl-home-jetson', children=[
                html.H2("Home Jetson Stats"),
                html.Button("Fetch Latest from Netdata", id='fetch-netdata-btn', 
                            style={'padding': '10px 20px', 'backgroundColor': '#007bff', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
            ], style={'display': 'block'}),

            # Work Log Controls
            html.Div(id='ctrl-work-logs', children=[
                html.H2("Work Log Analysis"),
                dcc.Upload(
                    id='upload-logs',
                    children=html.Div(['Drag and Drop or ', html.A('Select Log/CSV Files')]),
                    style={
                        'width': '100%', 'height': '80px', 'lineHeight': '80px',
                        'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '10px',
                        'textAlign': 'center', 'backgroundColor': '#f8f9fa'
                    }
                )
            ], style={'display': 'none'}),

            html.Hr(),
            html.Div(id='shared-display-area', style={'marginTop': '20px'})
        ], style={'width': '75%', 'padding': '20px', 'float': 'left'})
    ])
])

# 1. UI Toggle Logic: Show/Hide controls based on project
@app.callback(
    [Output('ctrl-home-jetson', 'style'),
     Output('ctrl-work-logs', 'style')],
    Input('project-selector', 'value')
)
def toggle_controls(project_id):
    if project_id == 'home_jetson':
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}

# 2. Sidebar Metadata & Library Refresh
@app.callback(
    [Output('project-metadata', 'children'),
     Output('data-library-list', 'children')],
    [Input('project-selector', 'value'),
     Input('data-update-signal', 'data')]
)
def update_sidebar(project_id, _signal):
    project = PROJECTS[project_id]
    metadata = html.Div([
        html.P(project['description']),
        html.Code(f"Template: {project['template']}", style={'fontSize': '10px'})
    ])
    
    project_dir = ensure_project_dir(project_id)
    files = sorted([f for f in os.listdir(project_dir) if f.endswith('.csv')], reverse=True)
    
    library = html.Div([
        html.A(f, id={'type': 'library-file', 'index': f}, 
               style={'cursor': 'pointer', 'color': '#0066cc', 'display': 'block', 'marginBottom': '5px', 'textDecoration': 'underline'})
        for f in files[:15]
    ]) if files else html.P("No files found.", style={'fontStyle': 'italic'})
        
    return metadata, library

# 3. Centralized Data Processing
@app.callback(
    [Output('shared-display-area', 'children'),
     Output('data-update-signal', 'data')],
    [Input('fetch-netdata-btn', 'n_clicks'),
     Input('upload-logs', 'contents'),
     Input({'type': 'library-file', 'index': dash.ALL}, 'n_clicks'),
     Input('project-selector', 'value')],
    [State('upload-logs', 'filename'),
     State('data-update-signal', 'data')],
    prevent_initial_call=False
)
def handle_data_actions(n_fetch, upload_contents, n_library_clicks, project_id, upload_filename, current_signal):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'] if ctx.triggered else 'initial'

    # ACTION: Fetch from Netdata
    if 'fetch-netdata-btn' in trigger_id:
        try:
            chart_map = {'system.cpu': 'CPU', 'mem.available': 'RAM', 'system.load': 'Load', 'cpu.cpufreq': 'Freq'}
            all_data = []
            for cid, lbl in chart_map.items():
                res = requests.get(f"http://netdata:19999/api/v1/data?chart={cid}&after=-3600&format=json", timeout=3)
                if res.status_code == 200:
                    js = res.json()
                    tmp = pd.DataFrame(js['data'], columns=['time'] + [f"{lbl} ({l})" for l in js['labels'][1:]])
                    tmp['time'] = pd.to_datetime(tmp['time'], unit='s')
                    all_data.append(tmp.set_index('time'))
            
            df = pd.concat(all_data, axis=1).sort_index().reset_index()
            save_path = os.path.join(ensure_project_dir('home_jetson'), f"netdata_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            df.to_csv(save_path, index=False)
            return render_data_summary(df, "Fetched new data from Netdata"), current_signal + 1
        except Exception as e:
            return html.Div(f"Netdata Error: {e}", style={'color': 'red'}), current_signal

    # ACTION: Upload File
    elif 'upload-logs' in trigger_id and upload_contents:
        content_type, content_string = upload_contents.split(',')
        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))
        save_path = os.path.join(ensure_project_dir(project_id), f"ingested_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(save_path, index=False)
        return render_data_summary(df, f"Ingested {upload_filename}"), current_signal + 1

    # ACTION: Load from Library
    elif 'library-file' in trigger_id:
        file_json = json.loads(trigger_id.split('.')[0])
        filename = file_json['index']
        df = pd.read_csv(os.path.join(ensure_project_dir(project_id), filename))
        return render_data_summary(df, f"Loaded from library: {filename}"), current_signal

    # ACTION: Switch Project or Initial Load
    else:
        project_dir = ensure_project_dir(project_id)
        files = sorted([f for f in os.listdir(project_dir) if f.endswith('.csv')], reverse=True)
        if files:
            df = pd.read_csv(os.path.join(project_dir, files[0]))
            return render_data_summary(df, f"Project: {project_id} (Latest data loaded)"), current_signal
        return html.P("Project empty. Ingest data to begin."), current_signal

def render_data_summary(df, message):
    return html.Div([
        html.Div(message, style={'color': 'green', 'fontWeight': 'bold', 'marginBottom': '10px'}),
        html.H5("Data Preview (Top 10):"),
        dash.dash_table.DataTable(
            data=df.head(10).to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_table={'overflowX': 'auto', 'marginBottom': '20px'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'backgroundColor': '#f4f4f4', 'fontWeight': 'bold'}
        ),
        dcc.Graph(
            figure=px.line(df, x=df.columns[0], y=df.columns[1:], title="Project Data Visualization") if not df.empty else {}
        )
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)