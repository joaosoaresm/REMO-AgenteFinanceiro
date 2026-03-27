# config.py
# Centraliza todas as configurações e caminhos do projeto.

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

class Config:
    SECRET_KEY       = os.getenv("SECRET_KEY", "dev-secret")
    DEBUG            = os.getenv("DEBUG", "true").lower() == "true"
    WEBHOOK_SECRET   = os.getenv("WEBHOOK_SECRET", "")
    TRANSACTIONS_FILE = DATA_DIR / "transactions.json"