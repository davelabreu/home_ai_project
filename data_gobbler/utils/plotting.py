import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

class PlotTemplates:
    """
    Encapsulates complex Plotly logic for specific project types.
    """

    @staticmethod
    def encoder_analysis_v6(df: pd.DataFrame, title: str = "Encoder Analysis"):
        """
        Standardized V6 Unified Figure for Encoder Data.
        Ports the sophisticated subplot logic from Saleae_Parser.ipynb.
        """
        # 1. Prepare Data
        # Ensure we have a time column (t)
        time_col = 't' if 't' in df.columns else 'Time [s]'
        if time_col not in df.columns:
            # Fallback to index if no time column found
            df = df.copy()
            df['t'] = np.arange(len(df))
            time_col = 't'

        # 2. Setup Subplots
        fig = make_subplots(
            rows=5, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(
                "Encoder A/B Pulses",
                "Rolling CV (Slip Detection)",
                "Velocity (pulses/s)",
                "Direction of Travel",
                "Position (Cumulative)"
            )
        )

        # 3. Add Traces
        # Row 1: A/B Phases
        if 'A Phase' in df.columns and 'B Phase' in df.columns:
            fig.add_trace(go.Scatter(x=df[time_col], y=df['A Phase'], name="A Phase", mode='lines'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df[time_col], y=df['B Phase'] + 1.2, name="B Phase", mode='lines'), row=1, col=1)

        # Row 2: CV (Scatter)
        if 'CV' in df.columns:
            # Color by stage if available, else just blue
            fig.add_trace(go.Scatter(x=df[time_col], y=df['CV'], name="CV", mode='markers', 
                                   marker=dict(size=4, color='orange')), row=2, col=1)

        # Row 3: Velocity
        v_col = 'Velocity' if 'Velocity' in df.columns else 'Velocity pulses/s'
        if v_col in df.columns:
            fig.add_trace(go.Scatter(x=df[time_col], y=df[v_col], name="Velocity", mode='lines'), row=3, col=1)

        # Row 4: Direction
        d_col = 'Direction' if 'Direction' in df.columns else 'Direction of Travel'
        if d_col in df.columns:
            fig.add_trace(go.Scatter(x=df[time_col], y=df[d_col], name="Direction", mode='lines'), row=4, col=1)

        # Row 5: Position
        if 'Position' in df.columns:
            fig.add_trace(go.Scatter(x=df[time_col], y=df['Position'], name="Position", mode='lines'), row=5, col=1)

        # 4. Styling & Layout
        fig.update_layout(
            height=1000,
            template="plotly", # Switched to standard theme
            title_text=f"<b>{title}</b>",
            showlegend=True,
            margin=dict(t=100, l=50, r=50, b=50),
            hovermode="x unified"
        )
        
        # Unlink y-axes for independent scaling
        fig.update_yaxes(matches=None)
        
        return fig
