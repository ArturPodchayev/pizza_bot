import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_IDS: list[int] = [
    int(i.strip())
    for i in os.getenv("ADMIN_IDS", "").split(",")
    if i.strip().isdigit()
]
DATABASE_URL: str = os.getenv("DATABASE_URL", "")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env файле")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не задан в .env файле")
