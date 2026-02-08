# Data Gobbler: Professional Dash & Plotly Coding Rules

These rules are derived from industry best practices and the `hellodash` reference architecture.

## 🏗️ 1. Layout & Aesthetic (Bootstrap First)
*   **The Container Rule**: Always wrap layouts in a `dbc.Container(fluid=True)`.
*   **Grid Mastery**: Use `dbc.Row` and `dbc.Col` exclusively for positioning. Use the `width` parameter for responsive sizing.
*   **Logical Grouping**: Use `dbc.Card` and `dbc.CardBody` to encapsulate related controls (e.g., Plotting Params, Project Selection).
*   **Sexy Styling**: Leverage Bootstrap utility classes (`mb-4`, `p-2`, `shadow-sm`, `rounded-3`) instead of custom style dictionaries whenever possible.
*   **Theming**: Use `dbc.themes.DARKLY` as the default. All Plotly figures must use the `template="plotly_dark"` or a mapped DBC template to maintain visual unity.

## 🧠 2. Callback Architecture (The "Modular" Way)
*   **Consolidation**: If multiple components depend on the same inputs, use a single callback with multiple outputs to reduce server round-trips.
*   **Input vs. State**: Use `Input` for things that should trigger a change (Buttons, Dropdown changes) and `State` for values that are just "along for the ride" (Slider values, Text inputs).
*   **Performance**: Use `clientside_callback` for purely visual toggles (e.g., collapsing a sidebar or changing a theme) to keep the UI snappy.
*   **Safety**: Always include guard clauses at the top of callbacks (e.g., `if not n_clicks: raise dash.exceptions.PreventUpdate`).

## 📊 3. Plotly & Data (Data is King)
*   **DataFrame Centric**: All ingestion must result in a clean `pandas.DataFrame`.
*   **High-Level First**: Start with `plotly.express` (`px`) for speed and clarity. Move to `graph_objects` (`go`) only when extreme low-level trace customization is required.
*   **The Library Pattern**: Load static project metadata (like `projects.json`) globally.
*   **Historical Recall**: Store project data in `projects/[project_id]/` as CSVs. Use `dcc.Store(storage_type='local')` to remember the user's active file selection across page refreshes.

## 📁 4. Modularity & Maintenance
*   **Pages Pattern**: Every major feature (Home, Analysis, Admin) gets its own file in `pages/`.
*   **Utilities**: Move heavy data processing (CSV cleaning, Netdata API calls) to `utils/data_manager.py`.
*   **Commenting**: Every function must have a docstring explaining its purpose, inputs, and outputs. Code blocks should explain the "Why," not just the "What."
