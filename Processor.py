from DataMaker import make_synthetic_data


def process_symbol(buddy, i):
    """
    Handles one iteration of data ingestion, signal generation, and trade logging for a symbol.

    This function:
    
    - Adds tick to buffer and candles
    - Updates visualizer

    Args:
        buddy (object): Assistant-like object managing state, strategy, trader, candles, etc.
        i (int): iteration number of loop
        
    """

    # Get tick data (synthetic)
    buddy.last_tick = make_synthetic_data(buddy.last_tick)

    # Update each candle timeframe with the tick
    for candle in buddy.candles.values():
        candle.add_tick(buddy.last_tick)

    # Get trade recommendation
    buddy.strat.make_rec()

    # plot render
    if i == 0:
        buddy.plotter.render_all()
