from strategies.StrategyManager import StrategyManager
import pandas as pd

def process_main_stock_data(df: pd.DataFrame) -> dict:
    """Process main stock data for visualization."""
    df = df.copy()  # Explicitly create a copy
    x_data = df['date'].tolist()
    df[['open', 'close', 'low', 'high']] = df[['open', 'close', 'low', 'high']].astype(float)
    candle_data = df[['open', 'close', 'low', 'high']].values.tolist()
    # print("Candle Data:", candle_data)
    close_prices = df['close'].astype(float).tolist()
    
    # Calculate moving averages
    ma5 = calculate_ma(5, close_prices)
    ma10 = calculate_ma(10, close_prices)
    ma20 = calculate_ma(20, close_prices)
    
    return {
        'x_data': x_data,
        'candle_data': candle_data,
        'close_prices': close_prices,
        'ma5': ma5,
        'ma10': ma10,
        'ma20': ma20
    }


def process_strategy_data(df, strategy_configs):
    """
    Process stock data using the provided strategy configurations.
    
    :param df: DataFrame containing stock data.
    :param strategy_configs: List of strategy configurations.
    :return: Dictionary with strategy names and calculated results.
    """
    results = {}
    manager = StrategyManager()

    df = df.copy()  # Explicitly create a copy
    numerical_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
    df = df[numerical_columns].copy()
    df = df.astype(float)

    for config in strategy_configs:
        strategy = manager.get_strategy(config["name"])
        if strategy:
            results[config["name"]] = strategy.calculate(df, **config["params"])
        else:
            results[config["name"]] = {"error": f"Strategy {config['name']} not found."}
    
    return results


def calculate_ma(period: int, data: list) -> list:
    """Calculate moving average for a given period."""
    ma = []
    sum_value = 0
    for i in range(len(data)):
        sum_value += data[i]
        if i >= period:
            sum_value -= data[i - period]
        if i >= period - 1:
            ma.append(sum_value / period)
        else:
            ma.append(-1)
    return ma
