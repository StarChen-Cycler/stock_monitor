import pandas as pd
from strategies.BaseStrategy import BaseStrategy

# MACD Strategy
class MACDStrategy(BaseStrategy):
    """
    MACD strategy to calculate the MACD line and the Signal line.
    """
    def calculate(self, df: pd.DataFrame, fast_period, slow_period, signal_period):
        df = df.copy()
        fast_ema = df['close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = df['close'].ewm(span=slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=signal_period, adjust=False).mean()

        return {
            "macd": macd.tolist(),
            "signal": signal.tolist()
        }

# RSI Strategy
class RSIStrategy(BaseStrategy):
    """
    RSI strategy to calculate the Relative Strength Index.
    """
    def calculate(self, data: pd.DataFrame, period: int = 5):
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss.replace(0, 0.0001)  # Prevent division by zero
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.tolist()
        rsi = replace_invalid(rsi)

        return rsi

# Volume-based Strategies
class HighestVOLStrategy(BaseStrategy):
    """
    This strategy checks if the volume of the current day is the highest in the last N days.
    """
    def calculate(self, df: pd.DataFrame, period: int):
        df = df.copy()
        df['rolling_max_vol'] = df['vol'].rolling(window=period).max()
        df['highest_vol_today'] = df['vol'] == df['rolling_max_vol']
        
        return {
            "highest_vol_today": df['highest_vol_today'].tolist()
        }

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

# Helper function for invalid values
def replace_invalid(arr):
    """Replace invalid values (NaN) with 0."""
    return [x if pd.notnull(x) else 0 for x in arr]
