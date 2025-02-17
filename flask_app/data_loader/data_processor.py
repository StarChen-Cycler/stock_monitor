from strategies.StrategyManager import StrategyManager
import pandas as pd

# Helper function to replace NaN values (can be reused in data_processor)
def replace_invalid(arr):
    """Replace invalid values (NaN) with 0."""
    return arr.fillna(0)

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


# def process_strategy_data(df, strategy_configs):
#     """
#     Process stock data using the provided strategy configurations.
    
#     :param df: DataFrame containing stock data.
#     :param strategy_configs: List of strategy configurations.
#     :return: Dictionary with strategy names and calculated results.
#     """
#     results = {}
#     manager = StrategyManager()

#     df = df.copy()  # Explicitly create a copy
#     numerical_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
#     df = df[numerical_columns].copy()
#     df = df.astype(float)

#     for config in strategy_configs:
#         strategy = manager.get_strategy(config["name"])
#         if strategy:
#             df_result = strategy.calculate(df, **config["params"])
#             # Convert the DataFrame result to list format for the front-end
#             results[config["name"]] = replace_invalid(df_result.iloc[:, 0]).tolist()
#         else:
#             results[config["name"]] = {"error": f"Strategy {config['name']} not found."}

#     print("results:",results[:500])
#     return results

def process_strategy_data(df: pd.DataFrame, strategy_configs: list) -> dict:
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

    # Loop over strategy configurations and process
    for config in strategy_configs:
        strategy = manager.get_strategy(config["name"])
        if strategy:
            # Get the required input params for the strategy
            input_params = strategy.get_input_parameters()

            # Adjust input parameters if they are missing
            adjusted_params = {param: config["params"].get(param, default) for param, default in input_params.items()}

            try:
                # Run the strategy with the adjusted parameters
                df_result = strategy.calculate(df, **adjusted_params)

                # Replace NaN values
                df_result = replace_invalid(df_result)

                # Get strategy configuration
                strategy_config = strategy.get_config()
                print(f"Strategy {strategy.name()} config: {strategy_config}")

                # Add results to the output dictionary based on strategy outputs
                for output_name, data in df_result.items():
                    print(f"Processing output {output_name} for strategy {strategy.name()}")
                    config_for_output = strategy_config.get(output_name, {
                        'type': 'line',
                        'color': '#000000',
                        'name': output_name
                    })
                    # print(f"Using config for {output_name}: {config_for_output}")
                    
                    results[output_name] = {
                        'data': data.tolist(),
                        'config': config_for_output
                    }

            except TypeError as e:
                results[config["name"]] = {"error": f"Error with strategy {config['name']}: {str(e)}"}
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
