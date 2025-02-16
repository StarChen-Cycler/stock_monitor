from strategies.BaseStrategy import BaseStrategy
import pandas as pd

class LowestVOLStrategy(BaseStrategy):
    """
    This strategy checks if the volume of the current day is the lowest in the last N days.
    """
    def calculate(self, df: pd.DataFrame, period: int):
        df = df.copy()
        df['rolling_min_vol'] = df['vol'].rolling(window=period).min()
        df['lowest_vol_today'] = df['vol'] == df['rolling_min_vol']
        
        return {
            "lowest_vol_today": df['lowest_vol_today'].tolist()
        }
