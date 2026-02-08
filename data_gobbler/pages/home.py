import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Welcome to Data Gobbler", className="display-3 fw-bold text-primary"),
                html.P(
                    "A modular analytics workbench for engineers that want to move fast",
                    className="lead",
                ),
                html.Hr(className="my-4"),
                html.P(
                    "This v2 architecture uses Dash Pages for scalability and Bootstrap for a professional UI.",
                    className="text-muted"
                ),
                html.Div([
                    dbc.Button("📥 Get Started: Ingest Data", id="home-open-wizard", color="success", size="lg", className="me-3"),
                    dbc.Button("📊 View Analysis", href="/work-logs", color="primary", size="lg", outline=True),
                ], className="mt-4")
            ], className="p-5 bg-dark border rounded-3 shadow")
        ], width=12)
    ], className="mt-5")
], fluid=True)

# Callback to allow the home button to also trigger the global wizard
@dash.callback(
    dash.Output("open-wizard-btn", "n_clicks"),
    dash.Input("home-open-wizard", "n_clicks"),
    prevent_initial_call=True
)
def trigger_wizard_from_home(n):
    return n