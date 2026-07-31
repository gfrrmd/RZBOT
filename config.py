import json
import os

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

BOT_USERNAME = os.getenv("BOT_USERNAME", "").replace("@", "").strip()

# API credentials milik admin (1 untuk semua user)
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]

RESTRICTED_CHANNELS_RAW = os.environ.get("RESTRICTED_CHANNELS", "[]")
try:
    RESTRICTED_CHANNELS: list = json.loads(RESTRICTED_CHANNELS_RAW)
except Exception:
    RESTRICTED_CHANNELS = []

DEVICE_MODEL = "RamsBot VIP"
SYSTEM_VERSION = "iOS 26.4"
APP_VERSION = "11.4.1"
LANG_CODE = "id"
SYSTEM_LANG_CODE = "id-ID"
