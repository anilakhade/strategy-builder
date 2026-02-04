from math import log, sqrt, erf
from datetime import date
from typing import List, Tuple


def _norm_cdf(x: float) -> float:
    """
    Standard normal CDF using error function.
    """
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


class ProbabilityEngine:
    """
    Computes Probability of Profit (PoP) using a lognormal model.
    """

    def __init__(
        self,
        spot: float,
        volatility: float,
        expiry: date,
        today: date | None = None,
    ):
        """
        spot       : current spot price
        volatility : annualized volatility (e.g. 0.18 for 18%)
        expiry     : option expiry date
        today      : defaults to today()
        """
        self.spot = float(spot)
        self.vol = float(volatility)
        self.expiry = expiry
        self.today = today or date.today()

        self.T = self._time_to_expiry()

        if self.T <= 0:
            raise ValueError("Expiry must be in the future")

    # -------------------------------------------------

    def probability_of_profit(self, breakevens: List[float]) -> float:
        """
        Returns probability (0–1) that final price lies in profit region.
        """
        if not breakevens:
            # No breakeven → always profit or always loss
            # Caller should interpret this case
            return 0.0

        breakevens = sorted(breakevens)

        if len(breakevens) == 1:
            be = breakevens[0]

            # Profit above or below BE depends on payoff slope
            # Convention: assume profit ABOVE breakeven
            return 1.0 - self._cdf_price(be)

        if len(breakevens) == 2:
            be1, be2 = breakevens
            return self._cdf_price(be2) - self._cdf_price(be1)

        raise ValueError("More than 2 breakevens not supported")

    # -------------------------------------------------
    # Internal helpers
    # -------------------------------------------------

    def _time_to_expiry(self) -> float:
        """
        Time to expiry in years.
        """
        days = (self.expiry - self.today).days
        return days / 365.0

    def _cdf_price(self, price: float) -> float:
        """
        CDF of lognormal price distribution at given price.
        """
        z = self._z_score(price)
        return _norm_cdf(z)

    def _z_score(self, price: float) -> float:
        """
        Converts price level to Z-score under lognormal model.
        """
        return (
            log(price / self.spot)
            + 0.5 * self.vol * self.vol * self.T
        ) / (self.vol * sqrt(self.T))
