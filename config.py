import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Credentials
LOGIN_EMAIL = os.getenv("LIGA_EMAIL", "fe0rkut@gmail.com")
LOGIN_PASS = os.getenv("LIGA_PASS", "466161Fe*")

# URLs
SITE_BASE_URL = "https://www.ligapokemon.com.br/"
LOGIN_URL = "https://www.ligapokemon.com.br/?view=logar"
COLLECTION_URL = "https://www.ligapokemon.com.br/?view=colecao/colecao"

# Paths
DATA_DIR = BASE_DIR / "data"
USER_DATA_DIR = BASE_DIR / "user_data"
COOKIES_FILE = DATA_DIR / "session_cookies.json"
CREDENTIALS_FILE = DATA_DIR / "credentials.json"
COSTS_FILE = DATA_DIR / "cards_costs.json"
CARD_HISTORY_FILE = DATA_DIR / "cards_history.json"
SALES_CONFIG_FILE = DATA_DIR / "sales_config.json"
REGISTERED_STORES_FILE = DATA_DIR / "registered_stores.json"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

import json

def get_credentials():
    email = os.getenv("LIGA_EMAIL", "fe0rkut@gmail.com")
    password = os.getenv("LIGA_PASS", "466161Fe*")
    if CREDENTIALS_FILE.exists():
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                email = data.get("email", email)
                password = data.get("password", password)
        except Exception:
            pass
    return email, password

def save_credentials(email, password):
    data = {"email": email.strip(), "password": password}
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return True

