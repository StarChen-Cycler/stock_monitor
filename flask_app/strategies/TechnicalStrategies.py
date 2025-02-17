import pandas as pd
# from BaseStrategy import BaseStrategy
from strategies.BaseStrategy import BaseStrategy
import os

# Helper function to replace NaN values (can be reused in data_processor)
def replace_invalid(arr):
    """Replace invalid values (NaN) with 0."""
    return arr.fillna(0)

class VolumeStrategy(BaseStrategy):
    """Volume strategy that returns the volume data."""
    
    def get_input_parameters(self):
        """Return the required input parameters for the Volume strategy."""
        return {
            "period": 20  # Default period for volume-based strategy
        }

    def calculate(self, df: pd.DataFrame, period: int = 20):
        """Return the volume data for the given period."""
        df = df.copy()
        
        # Simply return the volume data
        df['volume'] = df['vol']  # Assuming 'vol' is the column containing volume data
        
        return df[['volume']]  # Return DataFrame with volume column

    def name(self):
        """Return the name of the strategy in lowercase."""
        return "volume"

    def get_config(self):
        return {
            'volume': {
                'color': '#0f00ff',
                'type': 'bar',
                'name': 'Volume'
            }
        }


# MACD Strategy
class MACDStrategy(BaseStrategy):
    """MACD strategy to calculate the MACD line and the Signal line."""
    
    def get_input_parameters(self):
        """Return the required input parameters for the MACD strategy."""
        return {
            "fast_period": 12,  # Default period for fast EMA
            "slow_period": 26,  # Default period for slow EMA
            "signal_period": 9  # Default period for signal line
        }

    def calculate(self, df: pd.DataFrame, fast_period: int=12, slow_period: int=26, signal_period: int=9):
        df = df.copy()
        fast_ema = df['close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = df['close'].ewm(span=slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=signal_period, adjust=False).mean()

        # Return DataFrame with MACD and Signal values
        df['macd'] = macd
        df['signal'] = signal
        return df[['macd', 'signal']]  # Return DataFrame with calculated columns
    
    def name(self):
        """Return the name of the strategy in lowercase."""
        return "macd"

    def get_config(self):
        return {
            'macd': {
                'color': '#00ff00',
                'type': 'line',
                'name': 'MACD'
            },
            'signal': {
                'color': '#ffff00',
                'type': 'line',
                'name': 'Signal'
            }
        }

# RSI Strategy
class RSIStrategy(BaseStrategy):
    """RSI strategy to calculate the Relative Strength Index."""
    
    def get_input_parameters(self):
        """Return the required input parameters for the RSI strategy."""
        return {
            "period": 5  # Default period for RSI
        }

    def calculate(self, data: pd.DataFrame, period: int = 5):
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss.replace(0, 0.0001)  # Prevent division by zero
        rsi = 100 - (100 / (1 + rs))

        df = data.copy()
        df['rsi'] = replace_invalid(rsi)  # Replace NaN values

        return df[['rsi']]  # Return DataFrame with RSI column
    
    def name(self):
        """Return the name of the strategy in lowercase."""
        return "rsi"

    def get_config(self):
        return {
            'rsi': {
                'color': '#ff00ff',
                'type': 'line',
                'name': 'RSI'
            }
        }

# Volume-based Strategies
class HighestVOLStrategy(BaseStrategy):
    """This strategy checks if the volume of the current day is the highest in the last N days."""
    
    def get_input_parameters(self):
        """Return the required input parameters for the Highest Volume strategy."""
        return {
            "period": 20  # Default period for volume comparison
        }

    def calculate(self, df: pd.DataFrame, period: int = 20):
        df = df.copy()
        df['rolling_max_vol'] = df['vol'].rolling(window=period).max()
        df['highest_vol_today'] = (df['vol'] == df['rolling_max_vol']).astype(int)  # Convert boolean to 0/1

        return df[['highest_vol_today']]  # Return DataFrame with boolean value (0/1)
    
    def name(self):
        """Return the name of the strategy in lowercase."""
        return "highest_volume_today"

    def get_config(self):
        return {
            'highest_vol_today': {
                'color': '#ff0000',
                'type': 'line',
                'name': 'Highest Volume Today'
            }
        }

class LowestVOLStrategy(BaseStrategy):
    """This strategy checks if the volume of the current day is the lowest in the last N days."""
    
    def get_input_parameters(self):
        """Return the required input parameters for the Lowest Volume strategy."""
        return {
            "period": 20  # Default period for volume comparison
        }

    def calculate(self, df: pd.DataFrame, period: int = 20):
        df = df.copy()
        df['rolling_min_vol'] = df['vol'].rolling(window=period).min()
        df['lowest_vol_today'] = (df['vol'] == df['rolling_min_vol']).astype(int)  # Convert boolean to 0/1

        return df[['lowest_vol_today']]  # Return DataFrame with boolean value (0/1)
    
    def name(self):
        """Return the name of the strategy in lowercase."""
        return "lowest_volume_today"

    def get_config(self):
        return {
            'lowest_vol_today': {
                'color': '#0000ff',
                'type': 'line',
                'name': 'Lowest Volume Today'
            }
        }


class ExistHighestVOLStrategy(BaseStrategy):
    """This strategy checks how many days have passed since the highest volume appeared within the last N days."""
    
    def get_input_parameters(self):
        """Return the required input parameters for the Exist Highest Volume strategy."""
        return {
            "period": 7  # Default period for volume comparison
        }

    def calculate(self, df: pd.DataFrame, period: int = 100):
        df = df.copy()
        
        # Find the index of the highest volume in the rolling window
        df['highest_vol_idx'] = df['vol'].rolling(window=period).apply(lambda x: x.idxmax(), raw=False)
        # print(df['vol'].tail(20))
        # print(df['highest_vol_idx'].tail(20))
        # print(df['vol'].tail(20))
        # Calculate how many days have passed since the highest volume appeared
        # Use a safe approach to handle NaN values
        df['days_since_highest_vol'] = (df.index - df['highest_vol_idx']).fillna(0).astype(int)
        # print(df['days_since_highest_vol'].tail(20))
        # print(df[['days_since_highest_vol']])
        return df[['days_since_highest_vol']]  # Return DataFrame with the days passed
    
    def name(self):
        """Return the name of the strategy in lowercase."""
        return "days_since_last_high"

    def get_config(self):
        return {
            'days_since_highest_vol': {
                'color': '#0000ff',
                'type': 'line',
                'name': 'Days Since Highest Volume'
            }
        }



    
class ExistLowestVOLStrategy(BaseStrategy):
    """This strategy checks how many days have passed since the lowest volume appeared within the last N days."""
    
    def get_input_parameters(self):
        """Return the required input parameters for the Exist Lowest Volume strategy."""
        return {
            "period": 7  # Default period for volume comparison
        }

    def calculate(self, df: pd.DataFrame, period: int = 100):
        df = df.copy()
        
        # Find the index of the lowest volume in the rolling window
        df['lowest_vol_idx'] = df['vol'].rolling(window=period).apply(lambda x: x.idxmin(), raw=False)
        
        # Calculate how many days have passed since the lowest volume appeared
        # Use a safe approach to handle NaN values
        df['days_since_lowest_vol'] = (df.index - df['lowest_vol_idx']).fillna(0).astype(int)
        
        return df[['days_since_lowest_vol']]  # Return DataFrame with the days passed
    
    def name(self):
        """Return the name of the strategy in lowercase."""
        return "days_since_last_low"

    def get_config(self):
        return {
            'days_since_lowest_vol': {
                'color': '#ff0000',
                'type': 'line',
                'name': 'Days Since Lowest Volume'
            }
        }



# for testing
def load_parquet(file_path):
    """
    Load a Parquet file into a Pandas DataFrame.
    :param file_path: Path to the Parquet file.
    :return: Pandas DataFrame
    """
    try:
        df = pd.read_parquet(file_path)
        print(f"Loaded Parquet file from {file_path}")
        return df
    except Exception as e:
        print(f"Failed to load Parquet file: {e}")
        return None
    
if __name__ == "__main__":
    # Load sample stock data
    parquet_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\..', 'data', 'merged_data.parquet'))
    df = load_parquet(parquet_file_path)
    df = df[df['ts_code'] == "00001"]
    df = df.copy()  # Explicitly create a copy
    numerical_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
    df = df[numerical_columns].copy()
    # print(df)
    df = df.astype(float)
    
    # Calculate RSI
    strategy = ExistHighestVOLStrategy()
    ExistHighestStrategy = strategy.calculate(df)
    ExistHighestStrategy = replace_invalid(ExistHighestStrategy)
    