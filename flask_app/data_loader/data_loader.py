import os
import pandas as pd

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