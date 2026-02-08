# Data Gobbler: Professional Dash & Plotly Coding Rules

These rules are derived from industry best practices and the `hellodash` reference architecture.

## 🏗️ 1. Layout & Aesthetic (Bootstrap First)
*   **The Split-Pane Standard**: Use a fixed Left Sidebar for navigation, a Top Bar for global project controls, and a Central Canvas for data.
*   **The Inspector Pattern**: Use a right-hand `dbc.Offcanvas` for contextual settings. This panel must be triggered by a specific component (e.g., a Plot Card) and update global config stores.
*   **Grid Mastery**: Use `dbc.Row` and `dbc.Col` exclusively for positioning. Use the `width` parameter for responsive sizing.
*   **Theming**: Standard Plotly Light theme for figures to maintain engineering clarity.

## 🧠 2. Callback Architecture (The "Modular" Way)
*   **Consolidation**: If multiple components depend on the same inputs, use a single callback with multiple outputs to reduce server round-trips.
*   **Pattern Matching**: Use Dash Pattern Matching Callbacks (`ALL`, `MATCH`) to handle multiple dynamic Plot Cards efficiently.
*   **Performance**: Use `clientside_callback` for purely visual toggles.
*   **Safety**: Always include guard clauses at the top of callbacks.

## 📊 3. Plotly & Data (Data is King)
*   **The Canvas Rule**: The central workspace is a vertically scrollable list of independent Plot Cards.
*   **No-Code Customization**: Every plot must support trace toggling, header renaming, and type switching (line vs scatter) via the Inspector.
*   **Mapping Dictionaries**: Maintain a configuration dictionary in a `dcc.Store` to track user customizations for each plot card.
*   **DataFrame Centric**: All ingestion must result in a clean `pandas.DataFrame`.

## 📁 4. Modularity & Maintenance
*   **Pages Pattern**: Every major feature gets its own file in `pages/`.
*   **Fragmented Components**: Split complex UIs into logical fragments (e.g., `components/plot_card.py`, `components/inspector_panel.py`).
*   **Commenting**: Every function must have a docstring. Code blocks should explain the "Why," not just the "What."