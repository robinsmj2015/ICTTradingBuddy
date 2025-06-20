from datetime import datetime, time
import pytz

class SessionTimes:
    """
    Provides methods to classify trading sessions and assign
    time-of-day-based confidence levels for ICT scalping logic.
    """

    def __init__(self):
        pass

    @staticmethod
    def _get_scalping_session_code_(ts_str):
        """
        Assigns a session code based on the Eastern Time window.

        Args:
            ts_str (str): Timestamp in ISO 8601 format (UTC assumed if naive).

        Returns:
            str: One of "ny_kill", "reversal", or "other".
        """
        utc_dt = datetime.fromisoformat(ts_str)
        if utc_dt.tzinfo is None:
            utc_dt = pytz.utc.localize(utc_dt)

        eastern = utc_dt.astimezone(pytz.timezone("US/Eastern"))
        t = eastern.time()

        if time(7, 0) <= t < time(10, 0):
            return "ny_kill"
        elif time(10, 0) <= t < time(11, 30):
            return "reversal"
        else:
            return "other"

    @staticmethod
    def _ict_scalping_confidence_(ts_str):
        """
        Returns a confidence score (0-10) based on time-of-day market behavior.

        Args:
            ts_str (str): Timestamp in ISO 8601 format (UTC assumed if naive).

        Returns:
            int: Confidence level (higher means better conditions for scalping).
        """
        utc_dt = datetime.fromisoformat(ts_str)
        if utc_dt.tzinfo is None:
            utc_dt = pytz.utc.localize(utc_dt)

        eastern = utc_dt.astimezone(pytz.timezone("US/Eastern"))
        t = eastern.time()

        if time(9, 30) <= t <= time(10, 30):
            return 10  # Opening volatility
        elif time(10, 30) < t <= time(11, 30):
            return 7
        elif time(11, 30) < t <= time(14, 0):
            return 4
        elif time(14, 0) < t <= time(16, 15):
            return 6
        else:
            return 2  # Outside RTH or illiquid

