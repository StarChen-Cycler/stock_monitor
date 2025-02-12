def process_stock_data(df):
    x_data = df['date'].tolist()

    # Convert numerical columns to float
    df.loc[:, ['open', 'close', 'low', 'high']] = df[['open', 'close', 'low', 'high']].astype(float)
    candle_data = df[['open', 'close', 'low', 'high']].values.tolist()

    close_prices = df['close'].astype(float).tolist()

    # Calculate Moving Averages (replace -1 with None for ECharts compatibility)
    ma5 = calculate_ma(5, close_prices)
    ma5 = replace_invalid(ma5)
    ma10 = calculate_ma(10, close_prices)
    ma10 = replace_invalid(ma10)
    ma20 = calculate_ma(20, close_prices)
    ma20 = replace_invalid(ma20)

    return {
        "x_data": x_data,
        "candle_data": candle_data,
        "close_prices": close_prices,
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20
    }

def replace_invalid(arr):
    return [x if x != -1 else None for x in arr]

def calculate_ma(period, data):
    if period == 0 or not data:
        return []
    sum_value = 0
    ma = []
    for i in range(len(data)):
        sum_value += data[i]
        if i >= period:
            sum_value -= data[i - period]
        if i >= period - 1:
            ma.append(sum_value / period)
        else:
            ma.append(-1)
    return ma