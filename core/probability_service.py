from datetime import date
from typing import List, Dict

from core.spot import SpotFetcher
from core.probability import ProbabilityEngine


class ProbabilityService:
    """
    Computes Probability of Profit (PoP) for an option position.
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
        Returns PoP as percentage (0–100)
        """

        if not rows:
            raise ValueError("No positions provided")

        symbol = rows[0]["SYMBOL"]
        expiry = rows[0]["EXPIRY"]

        spot = self.spot_fetcher.get_spot(symbol)

        legs = [
            {
                "strike": r["STRIKE"],
                "opt": r["OPT"],
                "qty": r["T QTY"],
                "price": r["T PRICE"],
            }
            for r in rows
        ]

        engine = ProbabilityEngine(
            spot=spot,
            volatility=volatility,
            expiry=expiry,
            today=date.today(),
        )

        pop = engine.probability_of_profit(legs)
        return pop * 100.0
