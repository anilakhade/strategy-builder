from typing import List, Dict
from datetime import date
from kiteconnect import KiteConnect


class MarginEngine:
    """
    Zerodha margin engine with strict expiry validation.

    Rules:
    - Expiry must exactly match an exchange-listed expiry date
    - No month guessing
    - No fallback resolution
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
        expiry: date = row["EXPIRY"]

        candidates = []

        for inst in self.instruments:
            if inst.get("strike") != strike:
                continue
            if inst.get("instrument_type") != opt:
                continue
            if inst.get("name") != symbol:
                continue
            if inst.get("expiry") != expiry:
                continue

            candidates.append(inst)

        if len(candidates) == 1:
            return candidates[0]

        if not candidates:
            valid_expiries = sorted({
                inst["expiry"]
                for inst in self.instruments
                if inst.get("name") == symbol
            })

            if valid_expiries:
                exp_str = ", ".join(d.strftime("%d-%b-%Y") for d in valid_expiries)
                raise ValueError(
                    f"No contract found for {symbol} {expiry.strftime('%d-%b-%Y')}.\n"
                    f"Valid expiries are: {exp_str}"
                )

            raise ValueError(
                f"No contracts found at all for symbol {symbol}"
            )

        raise RuntimeError(
            f"Multiple contracts matched for {symbol} {expiry} {strike} {opt}"
        )
