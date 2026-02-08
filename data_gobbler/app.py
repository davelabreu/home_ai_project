import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.ingest_wizard import render_ingest_wizard

app = dash.Dash(
    __name__,
    use_pages=True, 
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True
)

# Shared Navbar for all pages
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Jetson Stats", href="/jetson-stats")),
        dbc.NavItem(dbc.NavLink("Work Logs", href="/work-logs")),
        dbc.Button("📥 Ingest Data", id="open-wizard-btn", color="success", className="ms-2"),
    ],
    brand="Data Gobbler v2",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4"
)

app.layout = dbc.Container([
    navbar,
    dash.page_container,
    render_ingest_wizard() # Globally available modal
], fluid=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
