import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def render_plot_card(plot_id: str, title: str = "New Plot"):
    """
    Renders a standalone card for an individual plot.
    Includes a 'Settings' button to trigger the contextual inspector.
    """
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col(html.H5(title, className="mb-0", id={'type': 'plot-title', 'index': plot_id}), width=10),
                dbc.Col(
                    dbc.Button(
                        html.I(className="bi bi-gear-fill"),
                        id={'type': 'open-inspector-btn', 'index': plot_id},
                        color="link",
                        size="sm",
                        className="text-muted p-0"
                    ),
                    width=2,
                    className="text-end"
                )
            ], align="center")
        ]),
        dbc.CardBody([
            dcc.Graph(
                id={'type': 'plot-graph', 'index': plot_id},
                config={'displayModeBar': True, 'responsive': True},
                style={'height': '400px'}
            )
        ])
    ], className="mb-4 shadow-sm plot-card", id={'type': 'plot-card-outer', 'index': plot_id})
