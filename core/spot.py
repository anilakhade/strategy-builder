from kiteconnect import KiteConnect
from datetime import date


class SpotFetcher:
    """
    Fetches current underlying price.

    Resolution order:
    1. Index → NSE index spot
    2. NSE stock → NSE cash LTP
    3. Commodity → nearest MCX futures LTP
    """

    INDEX_MAP = {
        "NIFTY": "NSE:NIFTY 50",
        "BANKNIFTY": "NSE:NIFTY BANK",
        "FINNIFTY": "NSE:NIFTY FIN SERVICE",
    }

    def __init__(self, kite: KiteConnect):
        self.kite = kite
        self._instruments = kite.instruments()

    # -------------------------------------------------

    def get_spot(self, symbol: str) -> float:
        symbol = symbol.upper()

        # ---------- Index ----------
        if symbol in self.INDEX_MAP:
            inst = self.INDEX_MAP[symbol]
            data = self.kite.ltp(inst)
            return float(data[inst]["last_price"])

        # ---------- NSE Stock ----------
        if self._is_nse_stock(symbol):
            inst = f"NSE:{symbol}"
            data = self.kite.ltp(inst)
            return float(data[inst]["last_price"])

        # ---------- Commodity ----------
        return self._get_commodity_future_price(symbol)

    # -------------------------------------------------

    def _is_nse_stock(self, symbol: str) -> bool:
        """
        Checks if symbol exists as NSE equity.
        """
        return any(
            inst for inst in self._instruments
            if inst["exchange"] == "NSE"
            and inst["tradingsymbol"] == symbol
            and inst["instrument_type"] == "EQ"
        )

    # -------------------------------------------------

    def _get_commodity_future_price(self, symbol: str) -> float:
        """
        Uses nearest expiry MCX futures as spot proxy.
        """
        today = date.today()

        futures = [
            inst for inst in self._instruments
            if inst["exchange"] == "MCX"
            and inst["name"] == symbol
            and inst["instrument_type"] == "FUT"
            and inst["expiry"] >= today
        ]

        if not futures:
            raise ValueError(f"No MCX futures found for {symbol}")

        fut = min(futures, key=lambda x: x["expiry"])
        key = f"{fut['exchange']}:{fut['tradingsymbol']}"

        data = self.kite.ltp(key)
        return float(data[key]["last_price"])
