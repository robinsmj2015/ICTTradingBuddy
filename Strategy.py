from InnerCircleTradingUtils import InnerCircleTradingUtils

class Strategy:
    """
    Base class for trading strategies. Provides a registration system
    and enforces implementation of core trading methods.
    """

    def __init__(self):
        self.ict_utils = InnerCircleTradingUtils()
        self._strategies = {}

    def register_strategy(self, name: str, strategy_class):
        """
        Registers a strategy class by name for later instantiation.

        Args:
            name (str): Name of the strategy.
            strategy_class (type): Class implementing the strategy.
        """
        self._strategies[name] = strategy_class

    def create(self, name: str, **kwargs):
        """
        Instantiates a registered strategy.

        Args:
            name (str): Strategy name.
            **kwargs: Arguments passed to the strategy's constructor.

        Returns:
            object: Instance of the strategy.
        """
        strategy_class = self._strategies.get(name)
        if not strategy_class:
            raise ValueError(f"Strategy '{name}' is not registered.")
        return strategy_class(**kwargs)

    # === Abstract Methods ===
    def make_rec(self):
        """
        Generates a trade recommendation.
        Subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement make_rec()")

    def get_entry(self):
        raise NotImplementedError("Subclasses must implement get_entry()")

    def get_stop_loss(self):
        raise NotImplementedError("Subclasses must implement get_stop_loss()")

    def get_take_profit(self):
        raise NotImplementedError("Subclasses must implement get_take_profit()")

    def get_num_contracts(self):
        raise NotImplementedError("Subclasses must implement get_num_contracts()")

    def get_timeout(self):
        raise NotImplementedError("Subclasses must implement get_timeout()")
