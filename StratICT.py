from Strategy import Strategy
from StopLoss import StopLoss
from TakeProfit import TakeProfit
from EntryMaker import EntryMaker
from ComputeIndicators import _get_inds_
import numpy as np


class StratICT(Strategy):
    """
    Implements an Inner Circle Trading (ICT)-inspired strategy for generating trade recommendations.
    
    Attributes:
        ict_threshold (int): Minimum number of zone confirmations needed to keep a zone.
        ict_merge_threshold (int): Tick range within which zones are merged (e.g. 5 ticks = 1.25 points for MNQ).
        buddy (object): Reference to the parent context (typically contains candles, last tick, and trader config).
    """

    def __init__(self, ict_threshold=3, ict_merge_threshold=5):
        """
        Initializes the strategy with threshold settings and helper classes.
        
        Args:
            ict_threshold (int): Number of votes/zones required to consider it valid.
            ict_merge_threshold (int): Number of ticks within which to merge zones.
        """
        super().__init__()
        self.buddy = None
        self.stop_loss = StopLoss()
        self.take_profit = TakeProfit()
        self.entry_maker = EntryMaker()
        self.ict_threshold = ict_threshold
        self.ict_merge_threshold = ict_merge_threshold


    def make_rec(self):
        """
        Generates a trade recommendation using ICT principles.
        
       
        """

        candle_manager = self.buddy.candles[1]
       
        tick = self.buddy.last_tick
        price = tick["last"]


        offset_dfs = {offset: tracker.df for offset, tracker in candle_manager.trackers.items() if len(tracker.df) >= self.buddy.data_gather_time}
        if not offset_dfs:
            self.buddy.recommendation.valid = False
            return

        all_obs = []
        all_fvgs = {"short": [], "long": []}
        all_liq = {"short": [], "long": []}
        scores = []

        for _, df in offset_dfs.items():
            candle = df.iloc[-1]

            atr_val = self.ict_utils.get_atr(df)
            order_blocks = self.ict_utils.detect_order_blocks(df)
            all_obs.extend(order_blocks)

            sweep_score = 0
            fvg_score = 0
            for direction in ["short", "long"]:
                liq = self.ict_utils.get_liquidity_pools(df, direction)
                fvg = self.ict_utils.get_fvg_targets(df, direction)
                all_liq[direction].extend(liq)
                all_fvgs[direction].extend(fvg)

                score_sweep = self.ict_utils.score_liquidity_sweep(df, direction, liq)
                score_fvg = self.ict_utils.score_fvg(price, fvg, direction)
                if abs(score_sweep) > abs(sweep_score): sweep_score = score_sweep
                if abs(score_fvg) > abs(fvg_score): fvg_score = score_fvg

            ob_score = self.ict_utils.score_order_blocks(price, order_blocks)
            imbalance = self.ict_utils.score_pressure_bias(tick.get("pressure"))
            dislocation = self.ict_utils.score_fv_dislocation(tick.get("fair_value_delta"))
            ind_score = self.get_inds(candle)

            session = self.ict_utils.ict_scalping_confidence(tick["timestamp"])
            volume_spike = self.score_volume_spike(df)
            session_volume = 0.5 * session + 0.5 * volume_spike

            components = [ob_score, sweep_score, fvg_score, imbalance, dislocation, ind_score, session_volume]
            score = int(round(sum(c for c in components if c is not None) / len(components), 0))
            scores.append(score)

        rec_val = int(round(sum(scores) / len(scores), 0))

        is_long = True if rec_val > self.buddy.trader.entry_ratio_threshold else False if rec_val < -self.buddy.trader.entry_ratio_threshold else None
        if is_long is None:
            self.buddy.recommendation.valid = False
            

        merged_obs = self.merge_zones(all_obs)
        merged_fvg = {d: self.merge_zones(all_fvgs[d]) for d in ["short", "long"]}
        merged_liq = {d: self.merge_zones(all_liq[d]) for d in ["short", "long"]}

        direction = "long" if is_long else "short"
        df0 = candle_manager.trackers[0].df
        candle0 = df0.iloc[-1]
        atr_val = self.ict_utils.get_atr(df0)
        vwap = candle0.get("VWAP")

        ob_range = self.ict_utils.get_nearest_ob_range(merged_obs, price, direction)
        fvg_zones = merged_fvg[direction]
        liq_pools = merged_liq[direction]

        entry = self.get_entry_price(candle0["close"], tick, direction, fvg_zones, merged_obs, atr_val, vwap)
        sl = self.get_stop_loss(df0, direction, ob_range, entry, atr_val, fvg_zones, liq_pools)
        tp = self.get_take_profit(entry, direction, ob_range, fvg_zones, liq_pools, atr_val, vwap)
        contracts = self.get_num_contracts(rec_val)
        timeout = self.get_timeout(atr_val)

        self.buddy.recommendation.update_trade(
            val=rec_val, position=direction, entry=entry, sl=sl, tp=tp,
            timestamp=tick["timestamp"], timeout=timeout, num_contracts=contracts
        )

        rec = self.buddy.recommendation
        rec.ict_indicators = {
            "order_blocks": ob_score,
            "liq_sweep": sweep_score,
            "fvg": fvg_score,
            "pressure_imbalance": imbalance,
            "fv_dislocation": dislocation,
            "atr": atr_val
        }
        rec.other_indicators = {"inds": ind_score}
        rec.ict_markers = {
            "liq_pools": merged_liq,
            "fvg_zones": merged_fvg,
            "obs": merged_obs,
            "ob_range": ob_range
        }


    def merge_zones(self, zones):
        """
        Merges overlapping or nearby zones into a single zone.
        
        Args:
            zones (list): A list of zone dicts or float pairs.
            
        Returns:
            list: A single merged zone, or empty if no valid input.
        """

        if not zones:
            return []

        # Case 1: List of dictionaries
        if isinstance(zones[0], dict):
            lows = [float(z["low"]) for z in zones if "low" in z]
            highs = [float(z["high"]) for z in zones if "high" in z]
            if not lows or not highs:
                return []
            return [{"low": min(lows), "high": max(highs)}]

        # Case 2: Flat list of alternating low/high values
        if isinstance(zones[0], (int, float, np.float64)):
            lows = [float(zones[i]) for i in range(0, len(zones), 2)]
            highs = [float(zones[i]) for i in range(1, len(zones), 2)]
            if not lows or not highs:
                return []
            return [{"low": min(lows), "high": max(highs)}]



    def zones_close(self, z1, z2):
        """
        Determines if two zones are close enough to merge based on the tick threshold.
        
        Args:
            z1 (dict): First zone with 'low'/'high' or 'start'/'end'.
            z2 (dict): Second zone.
        
        Returns:
            bool: True if zones are close enough, else False.
        """

        z1_low = z1.get("low", z1.get("start"))
        z1_high = z1.get("high", z1.get("end"))
        z2_low = z2.get("low", z2.get("start"))
        z2_high = z2.get("high", z2.get("end"))
        return abs(z1_low - z2_low) <= self.ict_merge_threshold * 0.25 and abs(z1_high - z2_high) <= self.ict_merge_threshold * 0.25


    def score_volume_spike(self, df) -> int:
        """
        Scores a spike in volume relative to the prior candles.
        
        Args:
            df (pd.DataFrame): Candle data.
        
        Returns:
            int: A score between 0 and 10 indicating volume increase.
        """

        if len(df) < 4: return 0
        current_vol = df.iloc[-1]["volume"]
        avg_vol = df.iloc[-4:-1]["volume"].mean()
        if avg_vol == 0: return 0
        ratio = current_vol / avg_vol
        scaled = min(ratio, 2.0)
        score = int(round((scaled - 1.0) / 1.0 * 10))
        return max(0, min(score, 10))

    def get_entry_price(self, last_close, tick, direction, fvg_zones, order_blocks, atr, vwap=None):
        """
        Computes the ideal entry price based on various ICT components.
        
        Returns:
            float: Rounded entry price.
        """
        return self.entry_maker._get_entry_price_(last_close, tick, direction, fvg_zones, order_blocks, atr, vwap)

    def get_stop_loss(self, df, direction, ob_range, price, atr_val, fvg_zones, liq_pools):
        """
        Calculates stop-loss level based on structure and volatility.
        
        Returns:
            float: Stop-loss price.
        """
        return self.stop_loss._get_stop_loss_(df, price, direction, ob_range, fvg_zones, atr_val, liq_pools)

    def get_take_profit(self, entry_price, direction, ob_range, fvg_targets, liq_pools, atr, vwap):
        """
        Calculates take-profit level using structure and expected R:R.
        
        Returns:
            float: Take-profit price.
        """
        return self.take_profit._get_take_profit_(entry_price, direction, ob_range, fvg_targets, liq_pools, atr, vwap)

    def get_num_contracts(self, rec) -> int:
        """
        Determines the number of contracts to enter based on recommendation score.
        
        Args:
            rec (int): Confidence score for trade.
        
        Returns:
            int: Number of contracts (1 to 3).
        """
        if abs(rec) > 8:
            return 3
        elif abs(rec) > 5:
            return 2
        else:
            return 1

    def get_timeout(self, atr_val) -> int:
        """
        Determines timeout in seconds based on volatility (ATR).
        
        Args:
            atr_val (float): Average True Range.
        
        Returns:
            int: Timeout duration in seconds.
        """

        if atr_val is None:
            return 300
        elif atr_val > 50:
            return 120
        elif atr_val > 20:
            return 180
        else:
            return 300
        
    def get_inds(self, candle) -> int:
        """
        Computes indicator-based confidence score.
        
        Args:
            candle (dict): Latest candle.
            symbol (str): Symbol for context (default: test).
        
        Returns:
            int: Score between -10 and +10.
        """
        
        return _get_inds_(candle)   

    