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
            'chart_group': 'volume_analysis',
            'chart_name': 'Volume Analysis',
            'outputs': {
                'volume': {
                    'color': '#FFA07A',  # Light salmon
                    'type': 'bar',
                    'name': 'Volume',
                    'order': 1
                }
            }
        }

    def is_self_based(self):
        """This strategy only requires individual stock data."""
        return True

# MACD Strategy
class MACDStrategy(BaseStrategy):
    """MACD strategy to calculate the MACD line, Signal line, and Histogram."""
    
    def get_input_parameters(self):
        """Return the required input parameters for the MACD strategy."""
        return {
            "fast_period": 12,  # Default period for fast EMA
            "slow_period": 26,  # Default period for slow EMA
            "signal_period": 9  # Default period for signal line
        }

    def calculate(self, df: pd.DataFrame, fast_period: int=12, slow_period: int=26, signal_period: int=9):
        df = df.copy()
        # Calculate MACD line (DIF)
        fast_ema = df['close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = df['close'].ewm(span=slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema  # This is the MACD line (DIF)
        
        # Calculate Signal line (DEA)
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        
        # Calculate Histogram (MACD - Signal)
        histogram = (macd - signal)*2

        # Return DataFrame with all components
        df['macd'] = macd
        df['signal'] = signal
        df['histogram'] = histogram
        return df[['macd', 'signal', 'histogram']]
    
    def name(self):
        """Return the name of the strategy in lowercase."""
        return "macd"

    def get_config(self):
        return {
            'chart_group': 'macd_analysis',  # Indicates these outputs should be in the same chart
            'chart_name': 'MACD Analysis',   # Display name for the chart
            'outputs': {
                'macd': {
                    'color': '#FF6B6B',  # Coral red
                    'type': 'line',
                    'name': 'MACD Line',
                    'order': 1  # Display order in the chart
                },
                'signal': {
                    'color': '#FFD700',  # Gold
                    'type': 'line',
                    'name': 'Signal Line',
                    'order': 2
                },
                'histogram': {
                    'type': 'bar',
                    'name': 'MACD Histogram',
                    'order': 0,  # Display behind the lines
                    'use_color_from': 'histogram'  # Special flag to use histogram coloring
                }
            }
        }

    def is_self_based(self):
        """This strategy only requires individual stock data."""
        return True

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
                'color': '#FFA500',  # Orange
                'type': 'line',
                'name': 'RSI'
            }
        }

    def is_self_based(self):
        """This strategy only requires individual stock data."""
        return True

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
                'color': '#FF4500',  # Orange red
                'type': 'line',
                'name': 'Highest Volume Today'
            }
        }

    def is_self_based(self):
        """This strategy only requires individual stock data."""
        return True

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
                'color': '#FFB6C1',  # Light pink
                'type': 'line',
                'name': 'Lowest Volume Today'
            }
        }

    def is_self_based(self):
        """This strategy only requires individual stock data."""
        return True

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
                'color': '#FF8C00',  # Dark orange
                'type': 'line',
                'name': 'Days Since Highest Volume'
            }
        }

    def is_self_based(self):
        """This strategy only requires individual stock data."""
        return True
    

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
                'color': '#DEB887',  # Burlywood (warm brown)
                'type': 'line',
                'name': 'Days Since Lowest Volume'
            }
        }

    def is_self_based(self):
        """This strategy only requires individual stock data."""
        return True


    
class MAStrategy(BaseStrategy):
    """Moving Average strategy to calculate various period MAs."""
    
    def get_input_parameters(self):
        """Return the required input parameters for the MA strategy."""
        return {
            "periods": [5, 10, 20]  # Default periods for MA calculations
        }

    def calculate(self, df: pd.DataFrame, periods: list = [5, 10, 20]):
        """Calculate moving averages for the specified periods."""
        df = df.copy()
        result_df = pd.DataFrame()
        
        for period in periods:
            ma_name = f'ma{period}'
            result_df[ma_name] = df['close'].rolling(window=period).mean().bfill().ffill()
        
        return result_df

    def name(self):
        """Return the name of the strategy in lowercase."""
        return "ma"

    def get_config(self):
        return {
            'chart_group': 'main_chart',
            'chart_name': 'Moving Averages',
            'outputs': {
                'ma5': {
                    'color': '#ff4500',  # Red-orange
                    'type': 'line',
                    'name': 'MA5',
                    'order': 1
                },
                'ma10': {
                    'color': '#06a7a0',  # Teal
                    'type': 'line',
                    'name': 'MA10',
                    'order': 2
                },
                'ma20': {
                    'color': '#3c763d',  # Green
                    'type': 'line',
                    'name': 'MA20',
                    'order': 3
                }
            }
        }

    def is_self_based(self):
        """This strategy only requires individual stock data."""
        return True
    

    
class RelativeReturnStrategy(BaseStrategy):
    """
    Strategy that calculates the relative return ratio of current price compared to 
    the N-day average price from M days ago.
    """
    
    def __init__(self):
        self.N = 5  # Default period for calculating moving average
        self.M = 20  # Default period for shifting the average

    def get_input_parameters(self):
        """Return the required input parameters for the Relative Return strategy."""
        return {
            "N": self.N,  # Default period for calculating moving average
            "M": self.M,  # Default period for shifting the average
            "column": "close"  # Default column to calculate returns for
        }

    def calculate(self, df: pd.DataFrame, N: int = 5, M: int = 20, column: str = "close"):
        """
        Calculate relative return ratio comparing current value to N-day average from M days ago.
        
        Args:
            df: DataFrame containing stock data
            N: The period for calculating the moving average
            M: The number of days to shift the average
            column: The column to calculate returns for
            
        Returns:
            DataFrame with relative return ratio column
        """
        self.N = N  # Store the user-defined N
        self.M = M  # Store the user-defined M
        
        df = df.copy()
        df = df.reset_index(drop=True)  # Reset index to ensure consistent calculations
        
        # Ensure the column exists
        if column not in df.columns:
            raise ValueError(f"Column {column} not found in DataFrame")
            
        # Calculate N-day moving average
        avg_name = f'avg_{column}_last_{N}_days'
        df[avg_name] = df[column].rolling(window=N, min_periods=1).mean()
        df[avg_name] = replace_invalid(df[avg_name])
        
        # Shift the average by M days
        shifted_avg_name = f'{avg_name}_shifted_{M}'
        df[shifted_avg_name] = df[avg_name].shift(M)
        df[shifted_avg_name] = replace_invalid(df[shifted_avg_name])
        
        # Calculate relative return ratio
        relative_return = f'relative_return_{N}_{M}'
        df[relative_return] = df[column] / df[shifted_avg_name].replace(0, float('nan')) - 1
        df[relative_return] = replace_invalid(df[relative_return])
        
        # Create result DataFrame with only the relative return column
        result_df = pd.DataFrame(index=df.index)
        result_df[relative_return] = df[relative_return]
        
        return result_df

    def name(self):
        """Return the name of the strategy in lowercase."""
        return "relative_return"

    def get_config(self):
        """Return the configuration for the Relative Return strategy."""
        return {
            'chart_group': 'return_analysis',
            'chart_name': 'Relative Return Analysis',
            'outputs': {
                f'relative_return_{self.N}_{self.M}': {  # Use stored N and M
                    'color': '#4169E1',  # Royal Blue
                    'type': 'line',
                    'name': f'Relative Return ({self.N},{self.M})',  # Updated to reflect dynamic values
                    'order': 1
                }
            }
        }

    def is_self_based(self):
        """This strategy only requires individual stock data."""
        return True



class RankPercentageStrategy(BaseStrategy):
    """
    Strategy that calculates normalized rank percentages across all stocks for each date.
    This is a cross-based strategy that requires data from all stocks to calculate ranks.
    """
    
    def get_input_parameters(self):
        """Return the required input parameters for the Rank Percentage strategy."""
        return {
            "column": "close"  # Default column to rank
        }

    def calculate(self, df: pd.DataFrame, column: str = "close"):
        """
        Calculate normalized rank percentages for each stock at each timestamp.
        
        Args:
            df: DataFrame containing all stocks data with MultiIndex [ts_code, date]
            column: Column name to calculate ranks for
            
        Returns:
            DataFrame with normalized rank percentage column
        """
        df = df.copy()
        
        # Ensure the column exists
        if column not in df.columns:
            raise ValueError(f"Column {column} not found in DataFrame")
        
        # Initialize result DataFrame with the same index as input
        result_df = pd.DataFrame(index=df.index)
        result_df['rank_percentage'] = 0.0
        
        # Get unique dates from the index
        if isinstance(df.index, pd.MultiIndex):
            dates = df.index.get_level_values('date').unique()
        else:
            # If somehow we don't have a MultiIndex, try to get dates from column
            if 'date' in df.columns:
                dates = df['date'].unique()
            else:
                raise ValueError("No date information found in DataFrame")
        
        # Calculate ranks for each date
        for date in dates:
            if isinstance(df.index, pd.MultiIndex):
                # Get data for this date using the MultiIndex
                date_data = df.xs(date, level='date', drop_level=False)
            else:
                # Fallback to column-based selection
                date_data = df[df['date'] == date]
            
            # Calculate ranks for this date
            ranks = date_data[column].rank(ascending=True)
            count = len(ranks)
            
            # Normalize to 0-100 range
            if count > 1:
                normalized_ranks = (ranks - 1) / (count - 1) * 100
            else:
                normalized_ranks = ranks * 0
            
            # Assign ranks back to result DataFrame
            result_df.loc[date_data.index, 'rank_percentage'] = normalized_ranks
        
        return result_df[['rank_percentage']]

    def name(self):
        """Return the name of the strategy in lowercase."""
        return "rank_percentage"

    def get_config(self):
        return {
            'chart_group': 'rank_analysis',
            'chart_name': 'Rank Percentage Analysis',
            'outputs': {
                'rank_percentage': {
                    'color': '#9370DB',  # Medium purple
                    'type': 'line',
                    'name': 'Rank Percentage',
                    'order': 1
                }
            }
        }

    def is_self_based(self):
        """This strategy requires data from all stocks for comparison."""
        return False




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
    
    if df is None or df.empty:
        print("Error: No data loaded from parquet file")
        exit(1)
        
    print("\nDataFrame Info:")
    print(df.info())
    print("\nAvailable ts_codes:")
    print(df['ts_code'].unique())
    
    # Test self-based strategy
    print("\nTesting self-based strategy (MA Strategy):")
    # Make sure we're using a ts_code that exists in the data
    available_ts_codes = df['ts_code'].unique()
    if len(available_ts_codes) == 0:
        print("Error: No ts_codes found in data")
        exit(1)
        
    test_ts_code = available_ts_codes[0]
    print(f"Using test ts_code: {test_ts_code}")
    
    single_stock_df = df[df['ts_code'] == test_ts_code].copy()
    if single_stock_df.empty:
        print(f"Error: No data found for ts_code {test_ts_code}")
        exit(1)
        
    numerical_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
    
    # Verify all required columns exist
    missing_columns = [col for col in numerical_columns if col not in single_stock_df.columns]
    if missing_columns:
        print(f"Error: Missing columns: {missing_columns}")
        print(f"Available columns: {single_stock_df.columns.tolist()}")
        exit(1)
    
    print("\nSample of single stock data:")
    print(single_stock_df[numerical_columns].head())
    
    single_stock_df_processed = single_stock_df[numerical_columns].copy()
    for col in numerical_columns:
        single_stock_df_processed[col] = pd.to_numeric(single_stock_df_processed[col], errors='coerce')
    
    ma_strategy = MAStrategy()
    ma_result = ma_strategy.calculate(single_stock_df_processed)
    print(f"\nMA Strategy Result (self-based):")
    print(ma_result.head())
    
    # Test cross-based strategy
    print("\nTesting cross-based strategy (Rank Percentage Strategy):")
    # For cross-based strategy, we need data from multiple stocks
    multi_stock_df = df.copy()
    
    # Add date column if not present
    if 'date' not in multi_stock_df.columns:
        print("Error: 'date' column not found in DataFrame")
        exit(1)
    
    # Convert numerical columns to float
    multi_stock_df_processed = multi_stock_df.copy()
    for col in numerical_columns:
        multi_stock_df_processed[col] = pd.to_numeric(multi_stock_df_processed[col], errors='coerce')
    
    print("\nSample of processed multi-stock data:")
    print(multi_stock_df_processed[['ts_code', 'date'] + numerical_columns].head())
    print(multi_stock_df_processed.head(), multi_stock_df_processed.tail())
    rank_strategy = RankPercentageStrategy()
    rank_result = rank_strategy.calculate(multi_stock_df_processed, column="close")
    print(f"\nRank Percentage Strategy Result (cross-based):")
    print(rank_result.head())
    
    # Print strategy types
    print("\nStrategy Types:")
    strategies = [MAStrategy(), MACDStrategy(), RSIStrategy(), VolumeStrategy(), 
                 HighestVOLStrategy(), LowestVOLStrategy(), ExistHighestVOLStrategy(),
                 ExistLowestVOLStrategy(), RelativeReturnStrategy(), RankPercentageStrategy()]
    
    for strategy in strategies:
        strategy_type = "Cross-based" if not strategy.is_self_based() else "Self-based"
        print(f"{strategy.name()}: {strategy_type}")