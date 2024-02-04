import enum

import asyncpg
from loguru import logger

DB_NAME = "prima_guard"
DB_USERNAME = "prima_guard"
DB_PASSWORD = "prima_guard"
DB_PORT = 5445
DB_HOST = "127.0.0.1"


async def create_conn():
    try:
        return await asyncpg.create_pool(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
                                         max_size=200)
    except Exception as error:
        logger.error(f"Ошибка при создании пула соединений: {error}")


async def get(pool, phone, description):
    try:
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT phone, description FROM feedback WHERE phone = $1 AND description = $2",
                phone, description)
    except Exception as e:
        logger.error(f"База данных вернула ошибку: {e}")


async def new(pool, phone, description):
    try:
        async with pool.acquire() as conn:
            await conn.execute("INSERT INTO feedback (phone, description, type_feedback) VALUES ($1, $2, $3)",
                               phone, description, "bad")
            logger.info(f"Добавлен отзыв: {phone}, {description}")
    except Exception as e:
        logger.error(f"База данных вернула ошибку: {e}")


class TypeFeedback(enum.IntEnum):
    good = 1
    middle = 0
    bad = -1
