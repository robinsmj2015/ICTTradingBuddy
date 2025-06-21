from Strategy import *

class Assistant:
    """
    Coordinates trading logic, tracking, and execution by linking together
    strategy modules, visualization, trade state, and buffers. Acts as the central
    orchestrator for processing ticks, managing state, and interfacing with the
    broader trading system components.

    Attributes:
        data_gather_time (datetime): The current timestamp used for evaluating indicators.
        symbol (str): The trading symbol
        points_to_dollars (float): Conversion factor for point value to dollars.
        trader: Trade execution manager.
        buff: Buffer that stores recent ticks or data windows.
        plotter: Charting/graphing utility.
        candles: CandleTracker instance or similar for aggregating ticks.
        strat: Strategy class instance used to generate entries and exits.
        recommendation: Object storing trade suggestions and logic output.
        FEE_PER_CONTRACT_2_WAYS (float): Round-trip commission/fee for each contract.
        in_market (bool): Flag indicating if a position is currently open.
        entry_row (dict or None): The row of data corresponding to the current/last entry.
        last_write_time (datetime or None): Timestamp of last write to log or sheet.
        last_tick (dict or None): Last processed tick data.
    """

    def __init__(
        self,
        data_gather_time: int,
        symbol: str,
        points_to_dollars: float,
        trader,
        buff,
        plotter,
        candles,
        strat,
        recommendation,
        FEE_PER_CONTRACT_2_WAYS: float = 2.00,
        
    ):
        """
        Initializes the Assistant object that ties together trading components 
        such as strategy, visualization, tick buffers, and trading logic.

        Args:
            data_gather_time (datetime): Time used for gathering and syncing indicators.
            symbol (str): Ticker symbol of the instrument being traded.
            points_to_dollars (float): Conversion ratio of index points to USD.
            trader: Trade executor component responsible for entering/exiting trades.
            buff: Tick buffer that stores recent market data.
            plotter: Chart plotting component.
            candles: Candle aggregator and indicator calculator.
            strat: Trading strategy class instance.
            recommendation: Strategy-generated recommendation container.
            FEE_PER_CONTRACT_2_WAYS (float): Total commission/fees per contract round trip.
        """
        # Core references
        self.data_gather_time = data_gather_time
        self.symbol = symbol
        self.points_to_dollars = points_to_dollars

        self.trader = trader
        self.buff = buff
        self.plotter = plotter
        self.candles = candles
        self.strat = strat
        self.recommendation = recommendation

        # Constants
        self.FEE_PER_CONTRACT_2_WAYS = FEE_PER_CONTRACT_2_WAYS

        # Trade state
        self.in_market = False
        self.entry_row = None
        self.last_write_time = None

        # Tick tracking
        self.last_tick = {}
