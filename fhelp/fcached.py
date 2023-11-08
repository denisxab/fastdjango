"""
Работа с Кешем
"""
import json
from typing import Any

from redis import Redis
from redis import asyncio as aioredis

from settings import REDIS_URL


class Cached:
    async def get_cached():
        ...

    async def get(self, key: str) -> Any | None:
        ...

    async def get_json(self, key: str) -> dict | None:
        res = await self.get(key)
        if res:
            return json.loads(res)

    async def set(self, key: str, value: Any):
        ...

    async def set_json(self, key: str, value: Any):
        await self.set(key, json.dumps(value, ensure_ascii=False))

    async def delete(self, key: str):
        ...

    async def delete_startswith(self, key: str):
        """Удалить все ключи которые начинаются на key"""
        ...


class RamServerCached(Cached):
    def __init__(self) -> None:
        self._data = {}

    async def get_cached(self):
        return self._data

    async def get(self, key: str) -> Any | None:
        return self._data.get(key)

    async def set(self, key: str, value: Any):
        self._data[key] = value

    async def delete(self, key: str):
        return self._data.pop(key, None)

    async def delete_startswith(self, key: str):
        # Создаем список ключей, которые нужно удалить
        keys_to_delete = [key for key in self._data.keys() if key.startswith(key)]

        # Удаляем эти ключи из словаря
        for key in keys_to_delete:
            del self._data[key]


class RedisCached(Cached):
    def __init__(self) -> None:
        self._redisConfConnect = dict(
            url=REDIS_URL
        )  # , encoding="utf8", decode_responses=True)

    async def get_cached(self):
        redis = aioredis.from_url(**self._redisConfConnect)
        yield redis

    async def get(self, key: str) -> Any | None:
        redis: Redis = aioredis.from_url(**self._redisConfConnect)
        res = await redis.get(key)
        if res:
            return res

    async def set(self, key: str, value: str | int | float | bool):
        redis: Redis = aioredis.from_url(**self._redisConfConnect)
        await redis.set(key, value)

    async def delete(self, key: str):
        redis: Redis = aioredis.from_url(**self._redisConfConnect)
        await redis.delete(key)

    async def delete_startswith(self, key: str):
        redis: Redis = aioredis.from_url(**self._redisConfConnect)
        keys_to_delete = await redis.keys(f"{key}*")
        if keys_to_delete:
            await redis.delete(*keys_to_delete)
