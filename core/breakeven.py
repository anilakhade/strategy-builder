from typing import List, Tuple


class BreakevenCalculator:
    """
    Computes exact breakeven points for option strategies (CE / PE only).
    """

    class Leg:
        def __init__(self, strike: float, opt: str, qty: int, premium: float):
            self.strike = strike
            self.opt = opt
            self.qty = qty
            self.premium = premium

        def coeff(self, S: float) -> Tuple[float, float]:
            if self.opt == "CE":
                if S < self.strike:
                    return 0.0, -self.qty * self.premium
                return self.qty, -self.qty * (self.strike + self.premium)

            # PE
            if S > self.strike:
                return 0.0, -self.qty * self.premium
            return -self.qty, self.qty * (self.strike - self.premium)

    # -----------------------------

    def __init__(self, rows: List[dict]):
        self.legs = [
            BreakevenCalculator.Leg(
                r["STRIKE"], r["OPT"], r["T QTY"], r["T PRICE"]
            )
            for r in rows
        ]

    # -----------------------------

    def breakevens(self) -> List[float]:
        strikes = sorted({l.strike for l in self.legs})
        points = [-1e18] + strikes + [1e18]

        bes = set()

        for i in range(len(points) - 1):
            lo, hi = points[i], points[i + 1]
            S = (lo + hi) / 2 if abs(lo) < 1e17 else hi - 1

            a = b = 0.0
            for leg in self.legs:
                da, db = leg.coeff(S)
                a += da
                b += db

            if abs(a) < 1e-12:
                continue

            x = -b / a
            if lo <= x <= hi:
                bes.add(round(x, 2))

        return sorted(bes)
