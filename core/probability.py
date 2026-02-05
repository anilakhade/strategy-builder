from math import log, sqrt, erf
from datetime import date
from typing import List, Tuple


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


class ProbabilityEngine:
    """
    Computes Probability of Profit (PoP) at expiry
    using exact payoff integration under lognormal model.
    """

    def __init__(
        self,
        spot: float,
        volatility: float,
        expiry: date,
        today: date | None = None,
    ):
        self.spot = float(spot)
        self.vol = float(volatility)
        self.expiry = expiry
        self.today = today or date.today()

        self.T = self._time_to_expiry()
        if self.T <= 0:
            raise ValueError("Expiry must be in the future")

    # -------------------------------------------------

    def probability_of_profit(self, legs: List[dict]) -> float:
        """
        legs: [{strike, opt, qty, price}]
        Returns probability in [0, 1]
        """

        # 1. Collect all critical points
        strikes = sorted({l["strike"] for l in legs})
        points = [0.0] + strikes + [1e12]

        profit_intervals: List[Tuple[float, float]] = []

        # 2. Check each interval midpoint
        for i in range(len(points) - 1):
            lo, hi = points[i], points[i + 1]

            if hi - lo < 1e-9:
                continue

            S = (lo + hi) / 2.0
            pnl = self._payoff(S, legs)

            if pnl >= 0:
                profit_intervals.append((lo, hi))

        # 3. Integrate probability over profit intervals
        prob = 0.0
        for lo, hi in profit_intervals:
            prob += self._cdf_price(hi) - self._cdf_price(lo)

        return max(0.0, min(1.0, prob))

    # -------------------------------------------------
    # Payoff
    # -------------------------------------------------

    @staticmethod
    def _payoff(S: float, legs: List[dict]) -> float:
        total = 0.0

        for l in legs:
            k = l["strike"]
            q = l["qty"]
            p = l["price"]

            if l["opt"] == "CE":
                intrinsic = max(S - k, 0.0)
            else:
                intrinsic = max(k - S, 0.0)

            total += q * (intrinsic - p)

        return total

    # -------------------------------------------------
    # Distribution
    # -------------------------------------------------

    def _time_to_expiry(self) -> float:
        return (self.expiry - self.today).days / 365.0

    def _cdf_price(self, price: float) -> float:
        if price <= 0:
            return 0.0
        z = self._z_score(price)
        return _norm_cdf(z)

    def _z_score(self, price: float) -> float:
        return (
            log(price / self.spot)
            + 0.5 * self.vol * self.vol * self.T
        ) / (self.vol * sqrt(self.T))
