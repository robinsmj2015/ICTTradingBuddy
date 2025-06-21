from TestDataMaker import make_test_data


def process_symbol(buddy):
    """
    Handles one iteration of data ingestion, signal generation, and trade logging for a symbol.

    This function:
    
    - Adds tick to buffer and candles
    - Updates visualizer
    - Makes a strategy-based recommendation
    - Writes trade data to dashboard 

    Args:
        buddy (object): Assistant-like object managing state, strategy, trader, candles, etc.
        
    """

    # Create synthetic data
    buddy.last_tick = make_test_data(buddy.last_tick)

    # Update each candle timeframe with the tick
    for candle in buddy.candles.values():
        candle.add_tick(buddy.last_tick)
    
    buddy.plotter.render_all()   

    # Get trade recommendation
    buddy.strat.make_rec()

    if buddy.recommendation.valid:
        rec = buddy.recommendation

        # Prepare trade data for logging
        rec_data = {
            "is_long": rec.position == "long",
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


