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
            Dataframes: Processed data.
        """
        pass
        raise NotImplementedError("Subclasses must implement the 'calculate' method.")

    @abstractmethod
    def get_input_parameters(self):
        """
        Get the required input parameters for the strategy.
        
        Returns:
            dict: Dictionary of parameter names and their default values.
        """
        pass

    @abstractmethod
    def name(self):
        """
        Get the name of the strategy.
        
        Returns:
            str: Strategy name in lowercase.
        """
        pass

    def get_config(self):
        """
        Get the configuration for the strategy's outputs.
        
        Returns:
            dict: Dictionary mapping output names to their visualization configs.
        """
        return {}

    @abstractmethod
    def is_self_based(self):
        """
        Identify whether the strategy is self-based or cross-based.
        Self-based: Only requires data from the individual stock.
        Cross-based: Requires data from multiple stocks at the same timestamp.
        
        Returns:
            bool: True if self-based, False if cross-based.
        """
        pass
