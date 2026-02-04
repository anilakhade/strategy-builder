from datetime import date
from typing import List, Dict

from core.breakeven import BreakevenCalculator
from core.spot import SpotFetcher
from core.probability import ProbabilityEngine


class ProbabilityService:
    """
    High-level service that computes Probability of Profit
    from positions using Zerodha spot.
    """

    def __init__(self, kite):
        self.kite = kite
        self.spot_fetcher = SpotFetcher(kite)

    # -------------------------------------------------

    def probability_of_profit(
        self,
        rows: List[Dict],
        volatility: float,
    ) -> float:
        """
        rows       : PositionBook.rows()
        volatility : annualized volatility (e.g. 0.18)

        Returns PoP as percentage (0–100).
        """

        if not rows:
            raise ValueError("No positions provided")

        # 1. Infer underlying symbol (assume all rows same)
        symbol = rows[0]["SYMBOL"]

        # 2. Infer expiry (assume all rows same)
        expiry = self._parse_expiry(rows[0]["EXPIRY"])

        # 3. Fetch spot from Zerodha
        spot = self.spot_fetcher.get_spot(symbol)

        # 4. Compute breakevens
        legs = [
            {
                "strike": r["STRIKE"],
                "opt": r["OPT"],
                "qty": r["T QTY"],
                "price": r["T PRICE"],
            }
            for r in rows
        ]

        breakevens = BreakevenCalculator(legs).breakevens()

        # 5. Compute probability
        engine = ProbabilityEngine(
            spot=spot,
            volatility=volatility,
            expiry=expiry,
            today=date.today(),
        )

        pop = engine.probability_of_profit(breakevens)

        return pop * 100.0

    # -------------------------------------------------

    @staticmethod
    def _parse_expiry(expiry_str: str) -> date:
        """
        Parses expiry string like '24-Feb' or '24-Feb-26'
        """
        from datetime import datetime

        expiry_str = expiry_str.strip()

        if expiry_str.count("-") == 2:
            return datetime.strptime(expiry_str, "%d-%b-%y").date()
        else:
            d = datetime.strptime(expiry_str, "%d-%b").date()
            return d.replace(year=date.today().year)
