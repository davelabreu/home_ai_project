import dash
from dash import dcc, html, Input, Output, State
import base64
import datetime
import io
import pandas as pd
import plotly.express as px

# Initialize the Dash application
# This server will run independently, as requested (separate microservice)
app = dash.Dash(__name__)
server = app.server # Expose the underlying Flask server for potential external WSGI use

# Define the layout of the Dash application
# Keeping the UI simple as requested, focusing on file upload.
app.layout = html.Div([
    html.H1("Data Analyzer Dashboard", style={'textAlign': 'center'}),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False # Allow only one file to be uploaded at a time
    ),
    
    html.Div(id='output-data-upload'), # Div to display output after upload
])

# Callback function to handle the uploaded file
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def parse_contents(contents, filename, date):
    """
    Parses the content of an uploaded file and displays a summary.
    This is a basic placeholder; future enhancements will include
    actual data processing and plotting.
    """
    if contents is not None:
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        try:
            # Assume the user uploads a CSV file for now.
            # In future, this can be extended to handle other formats (e.g., Excel, JSON).
            if 'csv' in filename:
                # Read CSV file into a pandas DataFrame
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            else:
                # If not a CSV, return an error message.
                return html.Div([
                    'There was an error processing this file. Only CSV files are supported for now.'
                ], style={'color': 'red'})

        except Exception as e:
            # Catch any other errors during file processing
            print(e)
            return html.Div([
                'There was an error processing this file: ', str(e)
            ], style={'color': 'red'})

        # Display a summary of the uploaded file and its DataFrame (simple UI)
        return html.Div([
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),
            
            html.H5("DataFrame Head:"),
            html.Pre(df.head().to_string()), # Display first 5 rows of the DataFrame
            
            html.H5("DataFrame Info:"),
            html.Pre(str(df.info())), # Display DataFrame info (columns, dtypes, non-null values)
            
            # Placeholder for future Plotly graph
            html.H5("Plotly Graph (Future Feature):"),
            dcc.Graph(
                id='example-graph',
                figure=px.scatter(df, x=df.columns[0], y=df.columns[1], title="Basic Scatter Plot (Placeholder)")
                if len(df.columns) > 1 else {}
            ) if not df.empty else html.Div("No data to plot")
        ])
    return html.Div() # Return empty Div if no file is uploaded yet


# Run the Dash application
if __name__ == '__main__':
    # The Dash app will run on http://127.0.0.1:8050/ by default.
    # debug=True enables the hot-reloading and debug tools.
    app.run(debug=True)
