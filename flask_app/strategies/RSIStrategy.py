from strategies.BaseStrategy import BaseStrategy
import pandas as pd
import os

class RSIStrategy(BaseStrategy):
    """
    RSI strategy to calculate the Relative Strength Index.
    """

    def calculate(self, data: pd.DataFrame, period: int = 5):
        """
        Calculate RSI for the given DataFrame.
        
        Parameters:
            data (DataFrame): Stock data with a 'close' column.
            period (int): Number of periods for RSI calculation.
            
        Returns:
            dict: RSI values.
        """
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

def replace_invalid(arr):
    """Replace invalid values (NaN) with -1."""
    return [x if pd.notnull(x) else 0 for x in arr]



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
    strategy = RSIStrategy()
    rsi = strategy.calculate(df)
    rsi = replace_invalid(rsi)
    
    # print(rsi)