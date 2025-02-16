from strategies.BaseStrategy import BaseStrategy
import pandas as pd

class HighestVOLStrategy(BaseStrategy):
    """
    This strategy checks if the volume of the current day is the highest in the last N days.
    """
    def calculate(self, df: pd.DataFrame, period: int):
        df = df.copy()  # Work on a copy of the dataframe to avoid changing the original
        df['rolling_max_vol'] = df['vol'].rolling(window=period).max()
        df['highest_vol_today'] = df['vol'] == df['rolling_max_vol']
        
        return {
            "highest_vol_today": df['highest_vol_today'].tolist()
        }
