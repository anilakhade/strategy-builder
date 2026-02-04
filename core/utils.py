def format_money(x: float) -> str:
    sign = "-" if x < 0 else ""
    x = abs(x)

    if x >= 1e7:
        return f"{sign}{x / 1e7:.2f} CR"
    if x >= 1e5:
        return f"{sign}{x / 1e5:.2f} Lac"
    if x >= 1e3:
        return f"{sign}{x / 1e3:.2f} K"

    return f"{sign}{x:.2f}"
