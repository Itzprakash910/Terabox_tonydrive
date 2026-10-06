import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", str(DATA_DIR / "downloads")))
DATA_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()}
FREE_DAILY_LIMIT = int(os.getenv("FREE_DAILY_LIMIT", "5"))
PREMIUM_DAILY_LIMIT = int(os.getenv("PREMIUM_DAILY_LIMIT", "100"))
FREE_MAX_MB = int(os.getenv("FREE_MAX_MB", "100"))
PREMIUM_MAX_MB = int(os.getenv("PREMIUM_MAX_MB", "2048"))
PREMIUM_DEFAULT_DAYS = int(os.getenv("PREMIUM_DEFAULT_DAYS", "30"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
