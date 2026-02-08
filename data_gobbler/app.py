import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import sys
import os

# Ensure the app directory is in the path for modular imports
sys.path.append(os.path.dirname(__file__))

from components.ingest_wizard import render_ingest_wizard
from components.inspector_panel import render_inspector_panel

app = dash.Dash(
    __name__,
    use_pages=True, 
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Define Sidebar Style
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#111", 
    "border-right": "1px solid #333",
    "z-index": 1000
}

# Define Content Style
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Data GOBBLER", className="display-6 fw-bold text-success mb-4"),
        html.Hr(style={"border-top": "1px solid #444"}),
        html.P("ENGINEERING WORKBENCH", className="text-muted small fw-bold"),
        dbc.Nav(
            [
                dbc.NavLink([html.I(className="bi bi-house-door me-2"), "Dashboard"], href="/", active="exact"),
                dbc.NavLink([html.I(className="bi bi-graph-up me-2"), "Work Logs"], href="/work-logs", active="exact"),
                dbc.NavLink([html.I(className="bi bi-cpu me-2"), "Jetson Stats"], href="/jetson-stats", active="exact"),
            ],
            vertical=True,
            pills=True,
            className="mb-4"
        ),
        html.Hr(style={"border-top": "1px solid #444"}),
        dbc.Button(
            [html.I(className="bi bi-plus-circle me-2"), "Quick Ingest"],
            id="open-wizard-btn",
            color="success",
            className="w-100 py-2",
            style={"border-radius": "10px"}
        ),
        html.Div([
            html.P("v0.4.0", className="text-muted mb-0", style={"font-size": "10px"}),
            html.P("Split-Pane Engine", className="text-muted", style={"font-size": "10px"}),
        ], style={"position": "absolute", "bottom": "1rem", "left": "1rem"})
    ],
    style=SIDEBAR_STYLE,
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    dcc.Store(id='wizard-trigger-store', data=0), 
    sidebar,
    html.Div(dash.page_container, style=CONTENT_STYLE),
    render_ingest_wizard(),
    render_inspector_panel() # Contextual settings sidebar
])

# Global callback to relay sidebar button to store
@app.callback(
    dash.Output('wizard-trigger-store', 'data'),
    dash.Input('open-wizard-btn', 'n_clicks'),
    dash.State('wizard-trigger-store', 'data'),
    prevent_initial_call=True
)
def relay_sidebar_trigger(n, current):
    if n is None:
        raise dash.exceptions.PreventUpdate
    return (current or 0) + 1

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
