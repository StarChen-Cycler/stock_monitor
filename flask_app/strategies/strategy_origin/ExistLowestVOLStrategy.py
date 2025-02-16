from strategies.BaseStrategy import BaseStrategy
import pandas as pd

class ExistLowestVOLStrategy(BaseStrategy):
    """
    This strategy checks how many days have passed since the lowest volume appeared
    within the last N days.
    """
    def calculate(self, df: pd.DataFrame, period: int):
        df = df.copy()
        df['rolling_min_vol'] = df['vol'].rolling(window=period).min()
        df['days_since_lowest_vol'] = df.apply(
            lambda row: (row.name - df[df['vol'] == row['rolling_min_vol']].index[-1]).days if row['vol'] == row['rolling_min_vol'] else None, axis=1
        )
        
        return {
            "days_since_lowest_vol": df['days_since_lowest_vol'].tolist()
        }
