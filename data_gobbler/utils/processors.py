import pandas as pd
import numpy as np
import re

class DataProcessors:
    """
    Modular data transformation logic for different project types.
    """

    @staticmethod
    def process_encoder_quadrature(df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Ports logic from Saleae_Parser.ipynb to decode A/B phases.
        Returns a DataFrame with Position, Velocity, and CV.
        """
        df = df_raw.copy()
        
        # 1. Identify and Rename Phase Columns
        phase_a_col = next((c for c in df.columns if re.search(r'a[\s_-]*phase', c, re.I)), None)
        phase_b_col = next((c for c in df.columns if re.search(r'b[\s_-]*phase', c, re.I)), None)
        
        if not phase_a_col or not phase_b_col:
            # Fallback to look for just 'A' and 'B' if 'Phase' isn't in title
            phase_a_col = next((c for c in df.columns if c.strip().upper() == 'A'), None)
            phase_b_col = next((c for c in df.columns if c.strip().upper() == 'B'), None)

        if not phase_a_col or not phase_b_col:
            raise ValueError("Could not find A/B Phase columns in data.")

        df.rename(columns={phase_a_col: 'A Phase', phase_b_col: 'B Phase'}, inplace=True)
        
        # 2. Quadrature Decoding
        a = df['A Phase'].values
        b = df['B Phase'].values
        steps = [0]
        direction = [0]
        
        for i in range(1, len(df)):
            prev = (a[i-1], b[i-1])
            curr = (a[i], b[i])
            if prev != curr:
                transition = (prev, curr)
                # Clockwise: 00->01, 01->11, 11->10, 10->00
                if transition in [((0,0),(0,1)), ((0,1),(1,1)), ((1,1),(1,0)), ((1,0),(0,0))]:
                    steps.append(1); direction.append(1)
                # Counter-Clockwise
                elif transition in [((0,0),(1,0)), ((1,0),(1,1)), ((1,1),(0,1)), ((0,1),(0,0))]:
                    steps.append(-1); direction.append(-1)
                else:
                    steps.append(0); direction.append(0)
            else:
                steps.append(0); direction.append(0)

        df['Step Change'] = steps
        df['Direction'] = direction
        df['Position'] = np.cumsum(steps)
        
        # 3. Time & Timing Stats
        time_col = next((c for c in df.columns if re.search(r'time', c, re.I)), df.columns[0])
        df['dT'] = df[time_col].diff().fillna(0)
        
        # Velocity (pulses/s)
        df['Velocity'] = df['Step Change'] / df['dT'].replace(0, np.nan)
        df['Velocity'] = df['Velocity'].fillna(0)

        # 4. Rolling CV (Coefficient of Variation) for Slip Detection
        # Only compute on rows where a pulse occurred
        df_pulses = df[df['Step Change'] != 0].copy()
        df_pulses['dT_pulse'] = df_pulses[time_col].diff()
        
        W = 10 # Window size from notebook
        df_pulses['mean_dT'] = df_pulses['dT_pulse'].rolling(W).mean()
        df_pulses['std_dT'] = df_pulses['dT_pulse'].rolling(W).std()
        df_pulses['CV'] = df_pulses['std_dT'] / df_pulses['mean_dT']
        
        # Map CV back to main dataframe
        df = df.merge(df_pulses[[time_col, 'CV']], on=time_col, how='left')
        
        return df
