from strategies.BaseStrategy import BaseStrategy
import pandas as pd

class MACDStrategy(BaseStrategy):
    """
    MACD strategy to calculate the MACD line and the Signal line.
    """
    
    def calculate(self, df: pd.DataFrame, fast_period, slow_period, signal_period):
        """
        Calculate the MACD and Signal line.
        
        :param df: DataFrame containing stock data.
        :param fast_period: Period for the fast EMA.
        :param slow_period: Period for the slow EMA.
        :param signal_period: Period for the Signal line.
        :return: Dictionary with MACD line and Signal line.
        """
        df = df.copy()
        fast_ema = df['close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = df['close'].ewm(span=slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        
        return {
            "macd": macd.tolist(),
            "signal": signal.tolist()
        }
