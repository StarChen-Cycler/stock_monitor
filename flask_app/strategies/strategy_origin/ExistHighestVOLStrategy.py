from strategies.BaseStrategy import BaseStrategy
import pandas as pd

class ExistHighestVOLStrategy(BaseStrategy):
    """
    This strategy checks how many days have passed since the highest volume appeared
    within the last N days.
    """
    def calculate(self, df: pd.DataFrame, period: int):
        df = df.copy()
        df['rolling_max_vol'] = df['vol'].rolling(window=period).max()
        df['days_since_highest_vol'] = df.apply(
            lambda row: (row.name - df[df['vol'] == row['rolling_max_vol']].index[-1]).days if row['vol'] == row['rolling_max_vol'] else None, axis=1
        )
        
        return {
            "days_since_highest_vol": df['days_since_highest_vol'].tolist()
        }
