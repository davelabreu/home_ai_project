import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Welcome to Data Gobbler", className="display-3"),
            html.P(
                "A modular analytics workbench for hardware telemetry and professional log analysis.",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P(
                "This v2 architecture uses Dash Pages for scalability and Bootstrap for a professional UI."
            ),
            dbc.Button("View Jetson Stats", href="/jetson-stats", color="primary"),
        ], width=12)
    ], className="mt-4 p-5 bg-light text-dark rounded-3")
])
