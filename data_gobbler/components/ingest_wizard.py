import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from utils.data_manager import DataManager
from utils.processors import DataProcessors
import base64
import io
import pandas as pd

def render_ingest_wizard():
    """
    Returns the layout for the Ingest Wizard Modal.
    """
    projects = DataManager.get_projects()
    
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("🚀 Data Ingestion Wizard")),
        dbc.ModalBody([
            # Step 1: Upload
            html.Div([
                html.Label("Step 1: Drop your CSV/Log file", className="fw-bold"),
                dcc.Upload(
                    id='wizard-upload',
                    children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                    style={
                        'width': '100%', 'height': '60px', 'lineHeight': '60px',
                        'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '10px',
                        'textAlign': 'center', 'margin': '10px 0'
                    }
                ),
                html.Div(id='wizard-file-info', className="text-muted small")
            ], className="mb-4"),

            # Step 2: Project Selection
            html.Div([
                html.Label("Step 2: Assign to Project", className="fw-bold"),
                dcc.Dropdown(
                    id='wizard-project-dropdown',
                    options=[{'label': p['name'], 'value': pid} for pid, p in projects.items()],
                    placeholder="Select a project...",
                    style={'color': 'black'} # Ensures text is readable in the dropdown list and selection
                ),
                html.Div(id='wizard-project-info', className="mt-2 small italic")
            ], className="mb-4"),

            # Step 3: Verification
            html.Div(id='wizard-preview-area', className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="wizard-cancel", color="secondary", className="me-2"),
            dbc.Button("Ingest & Process Data", id="wizard-submit", color="primary", disabled=True)
        ]),
    ], id="ingest-wizard-modal", is_open=False, size="lg")

# --- Callbacks for the Wizard ---

@callback(
    [Output("ingest-wizard-modal", "is_open"),
     Output("wizard-preview-area", "children"),
     Output("wizard-submit", "disabled"),
     Output("wizard-file-info", "children"),
     Output("url", "pathname"),
     Output("wizard-project-info", "children")],
    [Input("wizard-trigger-store", "data"),
     Input("wizard-cancel", "n_clicks"),
     Input("wizard-submit", "n_clicks"),
     Input("wizard-upload", "contents"),
     Input("wizard-project-dropdown", "value")],
    [State("ingest-wizard-modal", "is_open"),
     State("wizard-upload", "filename")],
    prevent_initial_call=True
)
def handle_wizard_logic(trigger_signal, n_cancel, n_submit, contents, project_id, is_open, filename):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, dash.no_update, True, "", dash.no_update, ""
    
    trigger = ctx.triggered[0]['prop_id']
    projects = DataManager.get_projects()
    project_info = ""
    
    # Selected Project Display logic
    if project_id:
        p = projects.get(project_id, {})
        project_info = dbc.Badge(f"Selected: {p.get('name')}", color="info", className="p-2")

    # 1. Open/Close Logic
    if "wizard-trigger-store" in trigger and trigger_signal:
        return True, "", True, "", dash.no_update, ""

    if "wizard-cancel" in trigger:
        return False, "", True, "", dash.no_update, ""

    # 2. Submission Logic (The actual 'Gobbling')
    if "wizard-submit" in trigger and contents and project_id:
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            # --- Project-Specific Processing ---
            template = projects[project_id].get('template')
            
            if template == 'encoder_quadrature':
                df = DataProcessors.process_encoder_quadrature(df)
            
            # Save to Silo
            new_filename = DataManager.save_dataframe(df, project_id, prefix="ingest")
            
            # Close modal and redirect to work-logs
            return False, dash.no_update, True, "", "/work-logs", ""
        except Exception as e:
            return True, dbc.Alert(f"❌ Ingestion Failed: {e}", color="danger"), False, filename, dash.no_update, project_info

    # 3. Preview/Verification Logic
    if contents and project_id:
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            preview = dbc.Alert([
                html.H5("✅ Data Verified"),
                html.P(f"Rows: {len(df)} | Columns: {', '.join(df.columns[:5])}..."),
                html.P(f"Target Project: {project_id}", className="mb-0")
            ], color="success")
            
            return True, preview, False, f"📄 {filename}", dash.no_update, project_info
        except Exception as e:
            return True, dbc.Alert(f"❌ Error reading file: {e}", color="danger"), True, "", dash.no_update, project_info

    if contents:
        return True, html.P("Please select a project to continue.", className="text-warning"), True, f"📄 {filename}", dash.no_update, project_info

    return is_open, dash.no_update, True, "", dash.no_update, project_info

# Note: The actual 'Saving' logic will be added in the next step to ensure 
# the DataManager integration is clean.
