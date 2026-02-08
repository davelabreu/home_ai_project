import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/jetson-stats')

layout = dbc.Container([
    html.H1("Jetson Stats", className="mt-4"),
    html.P("This page is under construction. It will soon feature live hardware telemetry analysis."),
    dbc.Alert("Telemetry integration pending.", color="info")
])
