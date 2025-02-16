import inspect
from strategies.TechnicalStrategies import *  # Import all strategies dynamically
import strategies.TechnicalStrategies as TechnicalStrategies
from strategies.BaseStrategy import BaseStrategy

class StrategyManager:
    """StrategyManager class that loads and manages different stock strategies."""
    
    _strategies = {}

    @classmethod
    def _load_strategies(cls):
        """Automatically load all strategies defined in the TechnicalStrategies module."""
        for name, obj in inspect.getmembers(TechnicalStrategies):
            # Check if the object is a class and is a subclass of BaseStrategy
            if inspect.isclass(obj) and issubclass(obj, BaseStrategy) and obj != BaseStrategy:
                strategy_instance = obj()  # Create an instance of the strategy class
                cls._strategies[strategy_instance.name()] = strategy_instance
        # print(cls._strategies)

    @classmethod
    def get_strategy(cls, name: str) -> BaseStrategy:
        """Retrieve a strategy instance by its name."""
        if not cls._strategies:
            cls._load_strategies()  # Load strategies when needed
        return cls._strategies.get(name.lower(), None)

    @classmethod
    def available_strategies(cls) -> list:
        """Get a list of available strategy names."""
        if not cls._strategies:
            cls._load_strategies()  # Load strategies when needed
        return list(cls._strategies.keys())
