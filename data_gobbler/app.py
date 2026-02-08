import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    use_pages=True, # Enables the multi-page 'pages/' directory logic
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True
)

# Shared Navbar for all pages
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Jetson Stats", href="/jetson-stats")),
        dbc.NavItem(dbc.NavLink("Work Logs", href="/work-logs")),
    ],
    brand="Data Gobbler v2",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4"
)

app.layout = dbc.Container([
    navbar,
    dash.page_container # This is where the content of each file in pages/ will render
], fluid=True)

if __name__ == '__main__':
    # Bind to 0.0.0.0 for Docker/Jetson accessibility
    app.run(host='0.0.0.0', port=8050, debug=True)
