import pandas as pd
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """Base interface for all trading strategies."""

    @abstractmethod
    def calculate(self, data: pd.DataFrame, **params):
        """
        Calculate the strategy's result.
        
        Parameters:
            data (DataFrame): Stock data with 'open', 'close', 'high', 'low', etc.
            **params: Additional parameters specific to the strategy.
            
        Returns:
            dict: Processed data and metadata.
        """
        pass
        raise NotImplementedError("Subclasses must implement the 'calculate' method.")
