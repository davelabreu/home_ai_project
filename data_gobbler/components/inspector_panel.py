import dash
from dash import html, dcc, callback, callback_context, ALL, MATCH, Input, Output, State
import dash_bootstrap_components as dbc
import json

def render_inspector_panel():
    return dbc.Offcanvas([
        html.Div(id="inspector-content")
    ],
    id="inspector-offcanvas",
    title="Plot Inspector",
    is_open=False,
    placement="end",
    style={"background-color": "#1a1a1a", "color": "white", "width": "400px"}
)

@callback(
    [Output("inspector-offcanvas", "is_open"),
     Output("inspector-content", "children")],
    [Input({'type': 'open-inspector-btn', 'index': ALL}, 'n_clicks')],
    [State("inspector-offcanvas", "is_open")],
    prevent_initial_call=True
)
def handle_inspector_toggle(n_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return is_open, dash.no_update
    
    # Check if any button was actually clicked
    if not any(n_clicks):
        return is_open, dash.no_update

    trigger_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    plot_index = trigger_id['index']
    
    content = html.Div([
        html.H4(f"Settings: {plot_index}"),
        html.Hr(),
        html.Label("Trace Visibility"),
        dbc.Checklist(
            options=[{"label": "Toggle All", "value": 1}],
            value=[1],
            id="master-trace-toggle",
            switch=True,
        ),
        html.Hr(),
        dbc.Button("Apply Changes", color="primary", className="w-100")
    ])
    
    return True, content

def build_trace_settings(columns, current_mappings=None):
    """
    Helper to generate the accordion items for each column/trace.
    """
    if not current_mappings:
        current_mappings = {}
        
    items = []
    for col in columns:
        items.append(
            dbc.AccordionItem([
                html.Div([
                    html.Label("Display Name", className="small mb-1"),
                    dbc.Input(
                        id={'type': 'trace-rename-input', 'index': col},
                        value=current_mappings.get(col, col),
                        size="sm",
                        className="mb-3"
                    ),
                    dbc.Checklist(
                        options=[{"label": "Visible", "value": 1}],
                        value=[1],
                        id={'type': 'trace-visibility-toggle', 'index': col},
                        switch=True
                    )
                ])
            ], title=f"Trace: {col}")
        )
    return dbc.Accordion(items, flush=True, start_collapsed=True)
