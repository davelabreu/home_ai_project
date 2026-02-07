# Data Analyzer Dashboard

This `README.md` provides information on setting up and running the Dash Plotly application for data ingestion and visualization. This application runs as a separate microservice.

## Purpose

The Data Analyzer Dashboard allows users to upload data files (currently CSV format) and view basic information about the data, including the first few rows and data types. It also provides a placeholder for interactive Plotly visualizations. This serves as a foundation for more advanced data analysis features.

## Project Structure

*   `app.py`: The main Dash Plotly application.
*   `requirements.txt`: Python dependencies for this Dash application.
*   `.venv/`: Python virtual environment for this application.

## Getting Started

To run the Data Analyzer Dashboard, you need Python 3 and its dependencies.

1.  **Navigate to the `data_analyzer` directory:**
    ```bash
    cd data_analyzer
    ```
2.  **Create and activate a Python virtual environment (if not already done):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Dash application:**
    ```bash
    python3 app.py
    ```
    The Dash app will typically run on `http://127.0.0.1:8050/`. Keep this terminal running.

## Usage

1.  Open your web browser and navigate to `http://127.0.0.1:8050/`.
2.  Click on "Drag and Drop or Select Files" to upload a CSV file.
3.  The dashboard will display the filename, last modified date, the head of the DataFrame, and its information.
4.  A basic scatter plot will be displayed if the uploaded CSV has at least two columns.

## Future Enhancements

*   Support for multiple file formats (Excel, JSON, etc.).
*   More advanced data manipulation and cleaning features.
*   A wider range of interactive Plotly visualizations.
*   Integration with the main `web_monitor` application.

## Contributing

Please adhere to the project's coding standards and conventions. Ensure your changes are well-tested and documented.

---
[Back to main project README](../README.md)
