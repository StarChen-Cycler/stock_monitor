from strategies.TechnicalStrategies import *
from strategies.BaseStrategy import BaseStrategy

class StrategyManager:
    """
    StrategyManager class that loads and manages different stock strategies.
    It maps strategy names to their respective classes and handles their instantiation.
    """

    _strategies = {
        'macd': MACDStrategy(),
        'rsi': RSIStrategy(),
        'highest_vol': HighestVOLStrategy(),
        'lowest_vol': LowestVOLStrategy(),
        'exist_highest_vol': ExistHighestVOLStrategy(),
        'exist_lowest_vol': ExistLowestVOLStrategy(),
        # Add new strategies here as needed
    }

    @classmethod
    def get_strategy(cls, name: str) -> BaseStrategy:
        """Retrieve a strategy instance by its name."""
        return cls._strategies.get(name.lower(), None)

    @classmethod
    def available_strategies(cls) -> list:
        """Get a list of available strategy names."""
        return list(cls._strategies.keys())
