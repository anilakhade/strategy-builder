from core.session import ZerodhaSession
from datetime import date


def main():
    session = ZerodhaSession()

    if not session.is_logged_in():
        print("❌ Not logged in to Zerodha")
        return

    kite = session.client()

    instruments = kite.instruments("NFO")
    print(f"Total NFO instruments: {len(instruments)}")

    symbol = "POWERGRID"

    # Step 1: find all option contracts for symbol
    rows = [
        inst for inst in instruments
        if inst.get("name") == symbol
        and inst.get("instrument_type") in ("CE", "PE")
    ]

    print(f"Total {symbol} option contracts found: {len(rows)}")

    if not rows:
        print("❌ No option contracts found at all for symbol")
        return

    # Step 2: show distinct expiries
    expiries = sorted({inst["expiry"] for inst in rows})
    print("\nAvailable expiries:")
    for e in expiries[:10]:
        print(" ", e)

    # Step 3: print a few contracts (strike + tradingsymbol)
    print("\nSample contracts:")
    rows = sorted(rows, key=lambda x: (x["expiry"], x["strike"]))[:20]

    for inst in rows:
        print(
            f"expiry={inst['expiry']}  "
            f"strike={inst['strike']}  "
            f"type={inst['instrument_type']}  "
            f"ts={inst['tradingsymbol']}"
        )


if __name__ == "__main__":
    main()
