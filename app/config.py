import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'fitbuddy.db'}"
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

ADMIN_TOKEN = os.getenv(
    "ADMIN_TOKEN",
    "change-this-token"
)

ALLOW_AI_FALLBACK = (
    os.getenv("ALLOW_AI_FALLBACK", "true").lower() == "true"
)