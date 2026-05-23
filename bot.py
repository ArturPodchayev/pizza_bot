import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

import db
from config import BOT_TOKEN, DATABASE_URL
from handlers import user, admin, humo_quiz

_fallback_router = Router()


@_fallback_router.message(F.text)
async def unhandled_text(message: Message) -> None:
    logger.info(f"UNHANDLED: user={message.from_user.id} text={message.text!r}")


async def main() -> None:
    await db.init_db(DATABASE_URL)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(humo_quiz.router)
    dp.include_router(_fallback_router)

    logger.info("Bot started")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.close_db()


if __name__ == "__main__":
    asyncio.run(main())
