import asyncio
import asyncpg
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

pool: asyncpg.Pool | None = None


async def init_db(dsn: str, retries: int = 5, delay: float = 3.0) -> None:
    global pool
    for attempt in range(1, retries + 1):
        try:
            pool = await asyncpg.create_pool(dsn, min_size=1, max_size=10)
            await _create_tables()
            logger.info("Database initialized")
            return
        except Exception as e:
            logger.warning(f"DB connect attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                await asyncio.sleep(delay * attempt)
    raise RuntimeError("Could not connect to PostgreSQL after retries")


async def _create_tables() -> None:
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            SERIAL PRIMARY KEY,
                telegram_id   BIGINT UNIQUE NOT NULL,
                username      TEXT,
                language      TEXT,
                full_name     TEXT,
                phone         TEXT,
                registered_at TEXT,
                is_active     SMALLINT DEFAULT 1
            )
        """)


async def close_db() -> None:
    global pool
    if pool:
        await pool.close()
        pool = None


async def get_user(telegram_id: int) -> asyncpg.Record | None:
    return await pool.fetchrow(
        "SELECT * FROM users WHERE telegram_id = $1", telegram_id
    )


async def upsert_user(
    telegram_id: int,
    username: str | None,
    language: str,
    full_name: str,
    phone: str,
) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await pool.execute(
        """
        INSERT INTO users (telegram_id, username, language, full_name, phone, registered_at)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (telegram_id) DO UPDATE SET
            username      = EXCLUDED.username,
            language      = EXCLUDED.language,
            full_name     = EXCLUDED.full_name,
            phone         = EXCLUDED.phone,
            registered_at = EXCLUDED.registered_at,
            is_active     = 1
        """,
        telegram_id, username, language, full_name, phone, now,
    )
    logger.info(f"User upserted: {telegram_id}")


async def get_all_active_users() -> list[asyncpg.Record]:
    return await pool.fetch("SELECT * FROM users WHERE is_active = 1")


async def get_users_by_language(lang: str) -> list[asyncpg.Record]:
    return await pool.fetch(
        "SELECT * FROM users WHERE is_active = 1 AND language = $1", lang
    )


async def get_users_count() -> int:
    return await pool.fetchval("SELECT COUNT(*) FROM users WHERE is_active = 1")


async def deactivate_user(telegram_id: int) -> None:
    await pool.execute(
        "UPDATE users SET is_active = 0 WHERE telegram_id = $1", telegram_id
    )
