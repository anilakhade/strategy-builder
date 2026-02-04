import os
import json
from datetime import date
from kiteconnect import KiteConnect
from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = "token.json"


class ZerodhaSession:
    """
    Zerodha session with daily access_token persistence.
    """

    def __init__(self):
        self.api_key = os.getenv("ZERODHA_API_KEY")
        self.api_secret = os.getenv("ZERODHA_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError("ZERODHA_API_KEY / ZERODHA_API_SECRET not set in .env")

        self.kite = KiteConnect(api_key=self.api_key)

        # Try auto-login
        if self._load_token():
            self.kite.set_access_token(self.access_token)

    # -------------------------------------------------

    def is_logged_in(self) -> bool:
        try:
            self.kite.profile()
            return True
        except Exception:
            return False

    # -------------------------------------------------

    def login_url(self) -> str:
        return self.kite.login_url()

    # -------------------------------------------------

    def generate_session(self, request_token: str) -> None:
        data = self.kite.generate_session(
            request_token,
            api_secret=self.api_secret
        )
        self.access_token = data["access_token"]
        self.kite.set_access_token(self.access_token)
        self._save_token()

    # -------------------------------------------------

    def client(self) -> KiteConnect:
        return self.kite

    # -------------------------------------------------
    # Token persistence
    # -------------------------------------------------

    def _save_token(self):
        payload = {
            "access_token": self.access_token,
            "date": date.today().isoformat()
        }
        with open(TOKEN_FILE, "w") as f:
            json.dump(payload, f)

    def _load_token(self) -> bool:
        if not os.path.exists(TOKEN_FILE):
            return False

        try:
            with open(TOKEN_FILE, "r") as f:
                data = json.load(f)

            if data.get("date") != date.today().isoformat():
                return False

            self.access_token = data.get("access_token")
            return True

        except Exception:
            return False
