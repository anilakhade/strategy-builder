from typing import List, Dict
from datetime import datetime, date
from kiteconnect import KiteConnect


class MarginEngine:
    """
    Zerodha margin engine with deterministic instrument resolution.

    Handles:
    - NSE equity options (decimal strikes supported)
    - MCX options
    """

    _instrument_cache = None

    def __init__(self, kite: KiteConnect):
        self.kite = kite

        if MarginEngine._instrument_cache is None:
            MarginEngine._instrument_cache = kite.instruments()

        self.instruments = MarginEngine._instrument_cache

    # -------------------------------------------------

    def compute_margin(self, positions: List[Dict]) -> Dict:
        orders = []

        for row in positions:
            orders.append(self._row_to_order(row))

        return self.kite.basket_order_margins(orders)

    # -------------------------------------------------

    def _row_to_order(self, row: Dict) -> Dict:
        qty = row["T QTY"]
        txn_type = "SELL" if qty < 0 else "BUY"
        abs_qty = abs(qty)

        instrument = self._resolve_instrument(row)

        return {
            "exchange": instrument["exchange"],
            "tradingsymbol": instrument["tradingsymbol"],
            "transaction_type": txn_type,
            "quantity": abs_qty,
            "product": "NRML",
            "order_type": "MARKET",
            "price": 0,
        }

    # -------------------------------------------------

    def _resolve_instrument(self, row: Dict) -> Dict:
        symbol = row["SYMBOL"].upper()
        strike = float(row["STRIKE"])
        opt = row["OPT"].upper()
        expiry = self._parse_expiry(row["EXPIRY"])

        # NSE equity option
        inst = self._resolve_nse_equity_option(symbol, expiry, strike, opt)
        if inst:
            return inst

        # MCX option
        inst = self._resolve_mcx_option(symbol, expiry, strike, opt)
        if inst:
            return inst

        raise ValueError(
            f"No contract found for {symbol} {expiry} {strike} {opt}"
        )

    # -------------------------------------------------
    # NSE EQUITY OPTIONS
    # -------------------------------------------------

    def _resolve_nse_equity_option(
        self,
        symbol: str,
        expiry: date,
        strike: float,
        opt: str,
    ):
        strike_str = self._format_equity_strike(strike)
        year = str(expiry.year)[-2:]
        month = expiry.strftime("%b").upper()

        ts = f"{symbol}{year}{month}{strike_str}{opt}"

        for inst in self.instruments:
            if (
                inst["exchange"] == "NFO"
                and inst["tradingsymbol"] == ts
            ):
                return inst

        return None

    # -------------------------------------------------
    # MCX OPTIONS
    # -------------------------------------------------

    def _resolve_mcx_option(
        self,
        symbol: str,
        expiry: date,
        strike: float,
        opt: str,
    ):
        year = str(expiry.year)[-2:]
        month = expiry.strftime("%b").upper()

        ts = f"{symbol}{year}{month}{int(strike)}{opt}"

        for inst in self.instruments:
            if (
                inst["exchange"] == "MCX"
                and inst["tradingsymbol"] == ts
            ):
                return inst

        return None

    # -------------------------------------------------

    @staticmethod
    def _format_equity_strike(strike: float) -> str:
        """
        NSE equity options use literal strikes.
        Examples:
        252   -> "252"
        252.5 -> "252.5"
        """
        if float(strike).is_integer():
            return str(int(strike))
        return str(strike)

    # -------------------------------------------------

    @staticmethod
    def _parse_expiry(expiry_str: str) -> date:
        expiry_str = expiry_str.strip()

        if expiry_str.count("-") == 2:
            return datetime.strptime(expiry_str, "%d-%b-%y").date()
        else:
            d = datetime.strptime(expiry_str, "%d-%b").date()
            return d.replace(year=date.today().year)
