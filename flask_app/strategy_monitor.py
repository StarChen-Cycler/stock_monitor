import os
import pandas as pd
from strategies.StrategyManager import StrategyManager
from models import db, StrategyResult
from data_loader.data_processor import get_params_hash, save_strategy_result
import hashlib
import json
from datetime import datetime
from flask import Flask
from config import Config
import time
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('strategy_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize DataFrame memory usage and convert data types efficiently."""
    df = df.copy()
    
    # Convert numerical columns to appropriate dtypes
    numerical_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
    for col in numerical_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce', downcast='float')
    
    # Convert date to datetime if it's not already
    if 'date' in df.columns:
        if pd.api.types.is_string_dtype(df['date']):
            # Convert string date in format 'YYYYMMDD' to datetime
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        elif not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
    
    return df

def batch_save_strategy_results(results: list):
    """Batch save strategy results to improve database performance."""
    try:
        db.session.bulk_save_objects(results)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error in batch saving results: {str(e)}")
        db.session.rollback()

def process_self_based_strategies_batch(stock_data: dict, strategies: list):
    """Process multiple self-based strategies for a stock in parallel."""
    results = []
    
    def process_single_strategy(strategy, df):
        try:
            default_params = strategy.get_input_parameters()
            params_hash = get_params_hash(default_params)
            result = process_stock_data(df, strategy, default_params)
            if result:
                return (strategy.name(), params_hash, result)
        except Exception as e:
            logger.error(f"Error processing strategy {strategy.name()}: {str(e)}")
        return None
    
    with ThreadPoolExecutor(max_workers=min(len(strategies), 4)) as executor:
        futures = [
            executor.submit(process_single_strategy, strategy, stock_data['df'])
            for strategy in strategies
        ]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                strategy_name, params_hash, data = result
                results.append({
                    'ts_code': stock_data['ts_code'],
                    'strategy_name': strategy_name,
                    'params_hash': params_hash,
                    'result_data': data
                })
    
    return results

def process_cross_based_strategies_batch(df: pd.DataFrame, strategies: list):
    """Process all cross-based strategies in one pass."""
    results = {}
    
    for strategy in strategies:
        try:
            default_params = strategy.get_input_parameters()
            params_hash = get_params_hash(default_params)
            df_result = process_cross_based_strategy(df, strategy, default_params)
            
            if df_result is not None:
                results[strategy.name()] = {
                    'result': df_result,
                    'params_hash': params_hash,
                    'strategy': strategy
                }
        except Exception as e:
            logger.error(f"Error processing cross-based strategy {strategy.name()}: {str(e)}")
    
    return results

def process_new_strategies():
    """Optimized version of strategy processing."""
    try:
        print("Starting optimized strategy processing...")
        app = Flask(__name__)
        app.config.from_object(Config)
        db.init_app(app)

        with app.app_context():
            # Load and optimize data
            parquet_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'merged_data.parquet'))
            df = pd.read_parquet(parquet_file_path)
            df = optimize_dataframe(df)
            
            # Get missing combinations
            missing_combinations = get_missing_strategy_combinations(df)
            if not missing_combinations:
                print("No missing strategy combinations found.")
                return

            manager = StrategyManager()
            total_combinations = sum(len(strategies) for strategies in missing_combinations.values())
            print(f"Processing {total_combinations} total combinations...")

            # Separate self-based and cross-based strategies
            all_strategies = {name: manager.get_strategy(name) for name in manager.available_strategies()}
            self_based_strategies = [s for s in all_strategies.values() if s and s.is_self_based()]
            cross_based_strategies = [s for s in all_strategies.values() if s and not s.is_self_based()]

            # Process cross-based strategies first (one pass for all stocks)
            if cross_based_strategies:
                print("Processing cross-based strategies...")
                cross_results = process_cross_based_strategies_batch(df, cross_based_strategies)
                
                # Save cross-based results for each stock
                for ts_code in tqdm(missing_combinations.keys(), desc="Saving cross-based results"):
                    stock_data = df[df['ts_code'] == ts_code]
                    if len(stock_data) < 2:
                        continue
                        
                    batch_results = []
                    for strategy_name, result_data in cross_results.items():
                        if strategy_name in missing_combinations[ts_code]:
                            result = create_strategy_result_entry(
                                result_data['result'], 
                                result_data['strategy'],
                                ts_code,
                                stock_data
                            )
                            if result:
                                batch_results.append(StrategyResult(
                                    ts_code=ts_code,
                                    strategy_name=strategy_name,
                                    params_hash=result_data['params_hash'],
                                    result_data=result
                                ))
                    
                    if batch_results:
                        batch_save_strategy_results(batch_results)

            # Process self-based strategies
            print("Processing self-based strategies...")
            first_stock = True
            with tqdm(total=len(missing_combinations), desc="Processing stocks") as pbar:
                for ts_code, missing_strategies in missing_combinations.items():
                    if first_stock:
                        print(f"\nFirst stock to process: {ts_code}")
                        input("Press Enter to process the first stock...")
                        first_stock = False
                    
                    stock_df = df[df['ts_code'] == ts_code].copy()
                    if len(stock_df) < 2:
                        pbar.update(1)
                        continue

                    # Filter for self-based strategies only
                    self_strategies_to_process = [
                        s for s in self_based_strategies 
                        if s.name() in missing_strategies
                    ]
                    
                    if self_strategies_to_process:
                        results = process_self_based_strategies_batch(
                            {'ts_code': ts_code, 'df': stock_df},
                            self_strategies_to_process
                        )
                        
                        if results:
                            batch_results = [
                                StrategyResult(
                                    ts_code=r['ts_code'],
                                    strategy_name=r['strategy_name'],
                                    params_hash=r['params_hash'],
                                    result_data=r['result_data']
                                )
                                for r in results
                            ]
                            batch_save_strategy_results(batch_results)
                    
                    pbar.update(1)

            print("Completed processing all strategies.")

    except Exception as e:
        print(f"Error in process_new_strategies: {str(e)}")
        logger.error(f"Error in process_new_strategies: {str(e)}")

def get_all_processed_strategies():
    """Get all unique strategy names that have been processed."""
    return {result[0] for result in StrategyResult.query.with_entities(StrategyResult.strategy_name).distinct()}

def get_missing_strategy_combinations(df: pd.DataFrame = None):
    """
    Check which combinations of ts_code and strategy are missing.
    Returns a dictionary mapping ts_codes to their missing strategies.
    """
    # Get all processed combinations
    processed_combinations = {
        (result.ts_code, result.strategy_name) 
        for result in StrategyResult.query.with_entities(
            StrategyResult.ts_code, 
            StrategyResult.strategy_name
        ).distinct()
    }
    
    # Get all available strategies
    manager = StrategyManager()
    available_strategies = manager.available_strategies()
    
    # If df is not provided, load it
    # if df is None:
    #     parquet_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'merged_data.parquet'))
    #     df = pd.read_parquet(parquet_file_path)
    
    # Get all unique ts_codes from the parquet file
    all_ts_codes = df['ts_code'].unique()
    
    # Find missing combinations
    missing_combinations = {}
    for ts_code in all_ts_codes:
        missing_strategies = set()
        for strategy_name in available_strategies:
            if (ts_code, strategy_name) not in processed_combinations:
                missing_strategies.add(strategy_name)
        if missing_strategies:
            missing_combinations[ts_code] = missing_strategies
            
    return missing_combinations

def process_stock_data(df: pd.DataFrame, strategy, default_params: dict) -> dict:
    """Process a single stock's data with a strategy."""
    df = df.copy()
    numerical_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
    df = df[numerical_columns].copy()
    df = df.astype(float)

    try:
        # Calculate strategy results
        df_result = strategy.calculate(df, **default_params)
        strategy_config = strategy.get_config()

        # Create the result entry
        result_entry = {
            'data': {},
            'config': {
                'chart_group': strategy_config.get('chart_group', strategy.name()),
                'chart_name': strategy_config.get('chart_name', strategy.name()),
                'outputs': {}
            }
        }

        # Process each output
        for output_name in df_result.columns:
            output_config = strategy_config.get('outputs', {}).get(output_name, {
                'type': 'line',
                'color': '#FFA500',
                'name': output_name,
                'order': 1
            })
            
            result_entry['data'][output_name] = df_result[output_name].tolist()
            result_entry['config']['outputs'][output_name] = output_config

        return result_entry

    except Exception as e:
        logger.error(f"Error processing strategy {strategy.name()}: {str(e)}")
        return None

def process_self_based_strategy(df: pd.DataFrame, strategy, default_params: dict, ts_code: str):
    """Process a self-based strategy for a single stock."""
    stock_df = df[df['ts_code'] == ts_code].copy()
    return process_stock_data(stock_df, strategy, default_params)

def process_cross_based_strategy(df: pd.DataFrame, strategy, default_params: dict) -> pd.DataFrame:
    """
    Process a cross-based strategy for all stocks at once.
    Returns the complete DataFrame with strategy results.
    """
    try:
        # Ensure numerical columns are float
        numerical_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
        df_processed = df.copy()
        
        # Ensure date column is properly formatted
        if 'date' in df_processed.columns:
            if pd.api.types.is_string_dtype(df_processed['date']):
                # Convert string date in format 'YYYYMMDD' to datetime
                df_processed['date'] = pd.to_datetime(df_processed['date'], format='%Y%m%d')
            elif not pd.api.types.is_datetime64_any_dtype(df_processed['date']):
                df_processed['date'] = pd.to_datetime(df_processed['date'])
        
        # Convert numerical columns
        for col in numerical_columns:
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
        
        # Set index to maintain alignment but keep date column
        if 'date' in df_processed.columns:
            df_processed = df_processed.set_index(['ts_code', 'date'])
        
        # Calculate strategy results for all stocks at once
        df_result = strategy.calculate(df_processed, **default_params)
        return df_result
    except Exception as e:
        logger.error(f"Error processing cross-based strategy {strategy.name()}: {str(e)}")
        return None

def create_strategy_result_entry(df_result: pd.DataFrame, strategy, ts_code: str, df: pd.DataFrame) -> dict:
    """
    Create a result entry dictionary for storing in the database.
    For cross-based strategies, filters the results for the specific ts_code.
    """
    strategy_config = strategy.get_config()
    result_entry = {
        'data': {},
        'config': {
            'chart_group': strategy_config.get('chart_group', strategy.name()),
            'chart_name': strategy_config.get('chart_name', strategy.name()),
            'outputs': {}
        }
    }

    # Get the data for this specific stock
    stock_data = df[df['ts_code'] == ts_code]

    # Process each output column
    for output_name in df_result.columns:
        output_config = strategy_config.get('outputs', {}).get(output_name, {
            'type': 'line',
            'color': '#FFA500',
            'name': output_name,
            'order': 1
        })
        
        # Get the data for this stock's dates
        stock_result = df_result.loc[stock_data.index]
        result_entry['data'][output_name] = stock_result[output_name].tolist()
        result_entry['config']['outputs'][output_name] = output_config

    return result_entry

# def process_new_strategies():
#     """
#     Monitor for new strategies and process them for all stocks.
#     Also checks for missing strategy-stock combinations.
#     """
#     try:
#         print("Checkpoint 1: Starting process_new_strategies")
#         app = Flask(__name__)
#         app.config.from_object(Config)
#         db.init_app(app)

#         with app.app_context():
#             print("Checkpoint 2: Flask app context initialized")
            
#             # Load the parquet data first
#             parquet_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'merged_data.parquet'))
#             print(f"Checkpoint 3: Loading data from {parquet_file_path}")
#             df = pd.read_parquet(parquet_file_path)
#             print(f"Checkpoint 4: Loaded data with shape {df.shape}")
            
#             # Validate data structure
#             required_columns = ['ts_code', 'date', 'open', 'high', 'low', 'close', 'vol', 'amount']
#             missing_cols = [col for col in required_columns if col not in df.columns]
#             if missing_cols:
#                 raise ValueError(f"Missing required columns: {missing_cols}")
            
#             # Remove any rows where ts_code is invalid
#             df = df[df['ts_code'].str.match(r'^[0-9A-Za-z]+$', na=False)]
            
#             # Convert numerical columns to appropriate types
#             numerical_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
#             for col in numerical_columns:
#                 df[col] = pd.to_numeric(df[col], errors='coerce')
            
#             # Drop rows with NaN values in critical columns
#             df = df.dropna(subset=['ts_code', 'date'] + numerical_columns)
            
#             print(f"Checkpoint 4b: Data shape after cleaning: {df.shape}")
#             print("Sample of cleaned data:")
#             print(df.head())
            
#             # Get missing combinations using the loaded DataFrame
#             missing_combinations = get_missing_strategy_combinations(df)
#             print(f"Checkpoint 5: Found {len(missing_combinations)} stocks with missing strategies")
            
#             if not missing_combinations:
#                 print("No missing strategy combinations found. Exiting...")
#                 return

#             manager = StrategyManager()
#             total_combinations = sum(len(strategies) for strategies in missing_combinations.values())
#             print(f"Total missing combinations to process: {total_combinations}")

#             with tqdm(total=total_combinations, desc="Processing all combinations") as main_pbar:
#                 first_stock = True
#                 for ts_code, missing_strategies in missing_combinations.items():
#                     if first_stock:
#                         print(f"\nFirst stock to process: {ts_code}")
#                         print(f"Number of strategies to process: {len(missing_strategies)}")
#                         input("Press Enter to process the first stock...")
#                         first_stock = False
                    
#                     stock_df = df[df['ts_code'] == ts_code].copy()
                    
#                     if len(stock_df) < 2:  # Require at least 2 data points
#                         print(f"Insufficient data for stock {ts_code}, skipping...")
#                         main_pbar.update(len(missing_strategies))
#                         continue

#                     for strategy_name in missing_strategies:
#                         strategy = manager.get_strategy(strategy_name)
#                         if not strategy:
#                             print(f"Strategy {strategy_name} not found, skipping...")
#                             main_pbar.update(1)
#                             continue

#                         try:
#                             default_params = strategy.get_input_parameters()
#                             params_hash = get_params_hash(default_params)

#                             if strategy.is_self_based():
#                                 result = process_stock_data(stock_df, strategy, default_params)
#                                 if result:
#                                     save_strategy_result(ts_code, strategy_name, params_hash, result)
#                             else:
#                                 # For cross-based strategy, we need all stocks' data
#                                 df_result = process_cross_based_strategy(df, strategy, default_params)
#                                 if df_result is not None:
#                                     result = create_strategy_result_entry(df_result, strategy, ts_code, df)
#                                     if result:
#                                         save_strategy_result(ts_code, strategy_name, params_hash, result)
#                         except Exception as e:
#                             print(f"Error processing strategy {strategy_name} for stock {ts_code}: {str(e)}")
#                             logger.error(f"Error processing strategy {strategy_name} for stock {ts_code}: {str(e)}")
                        
#                         main_pbar.update(1)

#             print("\nCheckpoint 6: Completed processing all missing combinations")

#     except Exception as e:
#         print(f"Error in process_new_strategies: {str(e)}")
#         logger.error(f"Error in process_new_strategies: {str(e)}")

def clear_all_strategy_data():
    """Clear all strategy results from the database."""
    try:
        print("Clearing all strategy data from database...")
        app = Flask(__name__)
        app.config.from_object(Config)
        db.init_app(app)

        with app.app_context():
            # Delete all records from StrategyResult table
            count = StrategyResult.query.delete()
            db.session.commit()
            print(f"Successfully deleted {count} strategy results from database.")
            return count
    except Exception as e:
        print(f"Error clearing strategy data: {str(e)}")
        logger.error(f"Error clearing strategy data: {str(e)}")
        return 0

def run_monitor(interval_minutes=60, clear_existing=False):
    """
    Run the strategy monitor continuously with a specified interval.
    
    :param interval_minutes: Minutes to wait between checks
    :param clear_existing: Whether to clear existing strategy data before starting
    """
    print(f"Starting strategy monitor with {interval_minutes} minute interval...")
    logger.info("Starting strategy monitor...")
    
    if clear_existing:
        deleted_count = clear_all_strategy_data()
        print(f"Cleared {deleted_count} existing strategy results.")
    
    while True:
        print("\n" + "="*50)
        print(f"Starting new monitoring cycle at {datetime.now()}")
        print("="*50)
        process_new_strategies()
        print(f"\nSleeping for {interval_minutes} minutes...")
        logger.info(f"Sleeping for {interval_minutes} minutes...")
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    run_monitor(clear_existing=True) 