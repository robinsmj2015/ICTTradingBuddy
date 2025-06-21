class Recommendation:
    """
    Stores the current trading recommendation, including entry setup,
    risk parameters, and scoring metadata for both ICT and other indicators.
    
    Attributes:
        symbol (str): The trading symbol
        buddy (object): Reference to the Assistant or main controller.
        val (float): The final recommendation confidence score.
        position (str): "long", "short", or None.
        entry (float): Entry price for the trade.
        sl (float): Stop loss price.
        tp (float): Take profit price.
        timestamp (str): Timestamp when recommendation was made.
        timeout (int or float): Max duration to stay in trade (seconds or minutes).
        num_contracts (int): Number of contracts to trade.
        other_indicators (dict): Scores from non-ICT indicators (e.g., RSI).
        ict_indicators (dict): Scores from ICT indicators (e.g., order blocks, FVG).
        ict_markers (dict): Visual and positional ICT zones for plotting.
    """

    def __init__(self, symbol):
        """
        Initialize a new recommendation object.

        Args:
            symbol (str): The trading symbol for which this recommendation applies.
        """
        self.symbol = symbol
        self.buddy = None


        self.val = None
        self.position = None
        self.entry = None
        self.sl = None
        self.tp = None
        self.timestamp = None
        self.timeout = None
        self.num_contracts = None

        self.other_indicators = {}
        self.ict_indicators = {}
        self.ict_markers = {}

    def reset(self):
        """
        Clears all current recommendation data while retaining the symbol.
        """
        self.__init__(self.symbol)

    def update_trade(self, val, position, entry, sl, tp, timestamp, timeout, num_contracts):
        """
        Populates the recommendation with trade parameters and sets it to valid.

        Args:
            val (float): Confidence score.
            position (str): "long" or "short".
            entry (float): Entry price.
            sl (float): Stop loss price.
            tp (float): Take profit price.
            timestamp (str): Timestamp of the recommendation.
            timeout (float): Duration until trade is invalidated or exited.
            num_contracts (int): Number of contracts to trade.
        """
        
        self.val = val
        self.position = position
        self.entry = entry
        self.sl = sl
        self.tp = tp
        self.timestamp = timestamp
        self.timeout = timeout
        self.num_contracts = num_contracts
