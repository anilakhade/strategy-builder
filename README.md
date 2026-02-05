# Strategy Builder

A practical options strategy analysis tool for Indian markets that computes:

- Net premium (P&L at entry)
- Exact breakeven points
- SPAN + Exposure margin (via Zerodha)
- Probability of profit (POP)
- Spot-based breakeven distance

Built for real trading workflows, not toy examples.

---

## What this project does

This tool allows you to:

1. Paste option positions directly (as traders copy from terminal / Excel)
2. Authenticate once with Zerodha
3. Instantly see:
   - Total premium (credit / debit)
   - Breakeven levels
   - Initial & final margin
   - SPAN and exposure breakdown
   - Probability of profit using spot + volatility

All computations are done locally, except:
- Margin (fetched from Zerodha)
- Spot price (fetched from Zerodha)

---

## Supported instruments (current stable version)

### Supported
- NSE index options (NIFTY, BANKNIFTY, FINNIFTY, etc.)
- NSE stock options
- Decimal strikes (e.g. 227.5, 232.5)
- Multi-leg strategies
- Credit / debit spreads, iron condors, ratios, etc.

### Not supported (intentionally, for now)
- Futures (FUT)

Futures support was explored but rolled back to keep the system stable.
It will be reintroduced cleanly in a future version.

---

## Input format (IMPORTANT)

This version expects headerless, space-separated rows.

Format:
SYMBOL EXPIRY STRIKE CE|PE QTY PRICE

### Example

```
ITC 24-Feb-2026 263.5 PE -19200 0.7
ITC 24-Feb-2026 273.5 PE  6400  1.1
ITC 24-Feb-2026 343.5 CE  6400  1.45
ITC 24-Feb-2026 353.5 CE -19200 0.8
```

- Quantity is signed:
  - Negative = sell
  - Positive = buy
- Price is option premium
- No headers required

---

## What each output means

### Net Value
Net premium paid or received at entry.
Credit is shown as positive.

### Breakeven
Exact price levels where strategy P&L = 0.
Computed analytically (not brute-force sampling).

### Margin
Fetched from Zerodha SPAN engine, split into:
- Initial Margin
- Final Margin
- SPAN
- Exposure

Matches actual broker margin, not approximations.

### Probability of Profit (POP)
Uses:
- Live spot price (Zerodha)
- User-provided annualized volatility
- Lognormal price assumption

POP represents the probability that expiry price lies in the profit region.
This is a model, not a guarantee.

---

## How to run the project

### Clone the repository
git clone https://github.com/anilakhade/strategy-builder.git
cd strategy-builder

### Create and activate virtual environment

Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

Windows:
python -m venv .venv
.venv\Scripts\Activate.ps1

### Install dependencies
pip install -r requirements.txt

---

## Environment variables

Create a .env file in the project root:

ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret

Never commit .env.

---

## Run the app
streamlit run run.py

This opens the app in your browser.

---

## Zerodha authentication flow

1. App shows a login URL
2. Click and login to Zerodha
3. Copy the request_token from redirected URL
4. Paste it into the app
5. Session is cached locally (token.json)

You do not need to re-login on every refresh unless the token expires.

---

## Project structure

```
strategy-builder/
├── core/
│   ├── positions.py        # Input parsing (options only)
│   ├── breakeven.py        # Exact breakeven math
│   ├── margin.py           # Zerodha margin engine
│   ├── probability.py      # POP math
│   ├── spot.py             # Live spot fetch
│   ├── session.py          # Zerodha auth handling
│   └── utils.py            # Formatting helpers
│
├── ui/
│   └── app.py              # Streamlit UI
│
├── run.py                  # App entry point
├── requirements.txt
└── README.md
```


---

## Design philosophy

- Correctness first
- Single source of truth for parsing
- No duplicated logic between UI and backend
- Real broker data over approximations
- Fail fast on invalid input

Designed for live trading analysis and gradual extension.

---

## Roadmap

- Futures (FUT) support
- Strategy comparison view
- Stress testing
- Scenario-based margin impact
- Historical POP validation

---
