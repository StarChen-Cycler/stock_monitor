from strategies.StrategyManager import StrategyManager
import pandas as pd
from models import db, StrategyResult
import hashlib
import json
from datetime import datetime, timedelta

def get_params_hash(params: dict) -> str:
    """Create a hash of strategy parameters for caching."""
    # Sort the params to ensure consistent hashing
    sorted_params = json.dumps(params, sort_keys=True)
    return hashlib.sha256(sorted_params.encode()).hexdigest()

def get_cached_result(ts_code: str, strategy_name: str, params_hash: str) -> dict:
    """Get cached strategy result if available and not too old."""
    cached = StrategyResult.query.filter_by(
        ts_code=ts_code,
        strategy_name=strategy_name,
        params_hash=params_hash
    ).first()
    
    if cached:
        # Check if result is less than 24 hours old
        if datetime.utcnow() - cached.updated_at < timedelta(hours=24):
            return cached.result_data
        # Delete old cache
        db.session.delete(cached)
        db.session.commit()
    return None

def save_strategy_result(ts_code: str, strategy_name: str, params_hash: str, result_data: dict):
    """Save or update strategy result in the database."""
    try:
        # Try to find existing record
        cached = StrategyResult.query.filter_by(
            ts_code=ts_code,
            strategy_name=strategy_name,
            params_hash=params_hash
        ).first()

        if cached:
            cached.result_data = result_data
            cached.updated_at = datetime.utcnow()
        else:
            new_result = StrategyResult(
                ts_code=ts_code,
                strategy_name=strategy_name,
                params_hash=params_hash,
                result_data=result_data
            )
            db.session.add(new_result)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving strategy result: {e}")

def process_main_stock_data(df: pd.DataFrame) -> dict:
    """Process main stock data for visualization."""
    df = df.copy()  # Explicitly create a copy
    x_data = df['date'].tolist()
    df[['open', 'close', 'low', 'high']] = df[['open', 'close', 'low', 'high']].astype(float)
    candle_data = df[['open', 'close', 'low', 'high']].values.tolist()
    close_prices = df['close'].astype(float).tolist()
    
    return {
        'x_data': x_data,
        'candle_data': candle_data,
        'close_prices': close_prices
    }

def process_strategy_data(df: pd.DataFrame, strategy_configs: list) -> dict:
    """
    Process stock data using the provided strategy configurations.
    Attempts to use cached results when available.
    
    :param df: DataFrame containing stock data.
    :param strategy_configs: List of strategy configurations.
    :return: Dictionary with strategy names and calculated results.
    """
    results = {}
    manager = StrategyManager()
    ts_code = df['ts_code'].iloc[0]  # Get the stock code

    df = df.copy()
    numerical_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
    df = df[numerical_columns].copy()
    df = df.astype(float)

    for config in strategy_configs:
        strategy = manager.get_strategy(config["name"])
        if not strategy:
            results[config["name"]] = {"error": f"Strategy {config['name']} not found."}
            continue

        try:
            # Get strategy configuration
            strategy_config = strategy.get_config()
            
            # Get and adjust input parameters
            input_params = strategy.get_input_parameters()
            adjusted_params = {param: config["params"].get(param, default) 
                             for param, default in input_params.items()}
            
            # print(f"Adjusted parameters: {adjusted_params}")
            # Generate hash for these parameters
            params_hash = get_params_hash(adjusted_params)
            
            # # Try to get cached result
            # cached_result = get_cached_result(ts_code, strategy.name(), params_hash)
            # if cached_result:
            #     results[strategy.name()] = cached_result
            #     continue

            # Calculate new results if no cache available
            df_result = strategy.calculate(df, **adjusted_params).bfill().ffill()

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

            # Save result to cache
            save_strategy_result(ts_code, strategy.name(), params_hash, result_entry)
            
            # Store in results
            results[strategy.name()] = result_entry

        except Exception as e:
            results[config["name"]] = {"error": f"Error with strategy {config['name']}: {str(e)}"}

    return results
