from typing import List, Dict
import re


class PositionBook:
    """
    Parses headerless, space-separated option positions.

    Supported row format (OPTIONS ONLY):

    SYMBOL EXPIRY STRIKE CE|PE QTY PRICE

    Example:
    ITC 24-Feb-26 263.5 PE -19200 0.7
    """

    def __init__(self, raw_text: str):
        self._rows: List[Dict] = []
        self._parse(raw_text)

    # -------------------------------------------------

    def rows(self) -> List[Dict]:
        return self._rows

    def total_value(self) -> float:
        return sum(r["VALUE"] for r in self._rows)

    # -------------------------------------------------

    def _parse(self, raw_text: str) -> None:
        if not raw_text.strip():
            raise ValueError("Empty input")

        lines = [l for l in raw_text.splitlines() if l.strip()]

        for line in lines:
            parts = re.split(r"\s+", line.strip())

            try:
                symbol = parts[0]
                expiry = parts[1]
                strike = float(parts[2])
                opt = parts[3].upper()

                if opt not in ("CE", "PE"):
                    raise ValueError("Only CE / PE supported")

                qty = int(parts[4])
                price = float(parts[5])

                self._rows.append({
                    "SYMBOL": symbol,
                    "EXPIRY": expiry,
                    "STRIKE": strike,
                    "OPT": opt,
                    "T QTY": qty,
                    "T PRICE": price,
                    "VALUE": -qty * price,
                })

            except Exception:
                raise ValueError(f"Invalid row: {line}")
