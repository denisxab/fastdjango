"""
Работа с Кешем
"""
import pickle
from typing import Any

from redis import Redis
from redis import asyncio as aioredis

from settings import REDIS_URL

redisConfConnect = dict(url=REDIS_URL)  # , encoding="utf8", decode_responses=True)


async def getRedis(key: str) -> Any | None:
    redis: Redis = aioredis.from_url(**redisConfConnect)
    res = await redis.get(key)
    if res:
        return pickle.loads(res)


async def setRedis(key: str, value: Any):
    redis: Redis = aioredis.from_url(**redisConfConnect)
    await redis.set(key, pickle.dumps(value))


async def deleteRedis(key: str):
    redis: Redis = aioredis.from_url(**redisConfConnect)
    await redis.delete(key)
