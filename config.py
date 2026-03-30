# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

class Config:
    SECRET_KEY        = os.getenv("SECRET_KEY", "dev-secret")
    DEBUG             = os.getenv("DEBUG", "true").lower() == "true"
    WEBHOOK_SECRET    = os.getenv("WEBHOOK_SECRET", "")
    TRANSACTIONS_FILE = DATA_DIR / "transactions.json"

    # Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama3-8b-8192")