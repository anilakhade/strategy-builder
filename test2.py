from datetime import date, timedelta

from core.probability import ProbabilityEngine


def main():
    # -----------------------------
    # MANUAL TEST CONFIG
    # -----------------------------
    spot = 275.0
    vol = 0.18
    expiry = date(2026, 2, 24)

    print("Testing POWERGRID strategy")
    print(f"Spot = {spot}, Vol = {vol*100:.1f}%, Expiry = {expiry}\n")

    # -----------------------------
    # POWERGRID STRATEGY (YOUR DATA)
    # -----------------------------
    legs = [
        {"strike": 250.0, "opt": "PE", "qty": -57000,  "price": 0.60},
        {"strike": 252.5, "opt": "PE", "qty": 19000,   "price": 0.75},
        {"strike": 255.0, "opt": "PE", "qty": -57000,  "price": 0.80},
        {"strike": 255.0, "opt": "PE", "qty": -57000,  "price": 0.50},
        {"strike": 257.5, "opt": "PE", "qty": 19000,   "price": 0.63},
        {"strike": 257.5, "opt": "PE", "qty": 19000,   "price": 1.00},
        {"strike": 260.0, "opt": "PE", "qty": -114000, "price": 0.76},
        {"strike": 262.5, "opt": "PE", "qty": 38000,   "price": 0.98},

        {"strike": 290.0, "opt": "CE", "qty": 95000,   "price": 3.12},
        {"strike": 295.0, "opt": "CE", "qty": -190000, "price": 2.09},
        {"strike": 300.0, "opt": "CE", "qty": 19000,   "price": 1.78},
        {"strike": 300.0, "opt": "CE", "qty": 76000,   "price": 1.63},
        {"strike": 305.0, "opt": "CE", "qty": -38000,  "price": 1.00},
        {"strike": 305.0, "opt": "CE", "qty": -114000, "price": 1.10},
        {"strike": 310.0, "opt": "CE", "qty": -57000,  "price": 0.70},
        {"strike": 310.0, "opt": "CE", "qty": -114000, "price": 0.73},
    ]

    # -----------------------------
    # PROBABILITY ENGINE
    # -----------------------------
    engine = ProbabilityEngine(
        spot=spot,
        volatility=vol,
        expiry=expiry,
        today=date.today(),
    )

    pop = engine.probability_of_profit(legs)

    print(f"Probability of Profit = {pop * 100:.2f}%\n")


if __name__ == "__main__":
    main()
