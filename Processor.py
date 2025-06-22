from DataMaker import make_synthetic_data
from BTCGetter import get_last_tick


def process_symbol(buddy, i):
    """
    Handles one iteration of data ingestion, signal generation, and trade logging for a symbol.

    This function:
    
    - Adds tick to buffer and candles
    - Updates visualizer
    - Makes a strategy-based recommendation
    - Writes trade data to dashboard 

    Args:
        buddy (object): Assistant-like object managing state, strategy, trader, candles, etc.
        i (int): iteration number of loop
        
    """

    # Get tick data

    # synthetic
    buddy.last_tick = make_synthetic_data(buddy.last_tick)

    #buddy.last_tick = get_last_tick()

    # Update each candle timeframe with the tick
    for candle in buddy.candles.values():
        candle.add_tick(buddy.last_tick)

    # Get trade recommendation
    buddy.strat.make_rec()


    # plot render
    if i == 0:
        buddy.plotter.render_all()

    
    rec = buddy.recommendation

    # Prepare trade data for logging
    rec_data = {
        "is_long": True if rec.position == "long" else None if rec.position is None else "short",
        "confidence": rec.val,
        "entry": rec.entry,
        "stop_loss": rec.sl,
        "timeout": rec.timeout,
        "take_profit": rec.tp,
        "num_contracts": rec.num_contracts 
    }

    # Write recommendation to buffer
    buddy.buff.write_recs_to_buff(rec_data)
    buddy.trader.check_trading(buddy.data_gather_time)
    


