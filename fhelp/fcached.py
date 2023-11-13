import json
from typing import Any

from redis import asyncio as aioredis

from settings import SettingsFastApi

settings = SettingsFastApi()


class BaseCached:
    async def get_cached(self):
        """Получить объект взаимодействие с кешем, использовать в fastapi.Depends"""
        ...

    async def get(self, key: str) -> Any | None:
        """Получить значение по ключу"""
        ...

    async def get_json(self, key: str) -> dict | None:
        """Получить значение из формате JSON в dict"""
        res = await self.get(key)
        if res:
            return json.loads(res)

    async def set(self, key: str, value: Any):
        """Вставить значение"""
        ...

    async def set_json(self, key: str, value: Any):
        """Вставить значение в формате JSON"""
        await self.set(key, json.dumps(value, ensure_ascii=False))

    async def delete(self, key: str):
        """Удалить ключ"""
        ...

    async def delete_startswith(self, startswith_key: str):
        """Удалить все ключи которые начинаются на key"""
        ...


class RamServerCached(BaseCached):
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

    async def delete_startswith(self, startswith_key: str):
        keys_to_delete = [
            key for key in self._data.keys() if key.startswith(startswith_key)
        ]
        for startswith_key in keys_to_delete:
            del self._data[startswith_key]


class RedisCached(BaseCached):
    DEFAULT_EXPIRE = 60 * 3

    def __init__(self, redis_url: str = settings.REDIS_URL) -> None:
        self._redisConfConnect = dict(url=redis_url)

    async def get_cached(self):
        async with aioredis.from_url(**self._redisConfConnect) as redis:
            yield redis

    async def get(self, key: str) -> Any | None:
        async with aioredis.from_url(**self._redisConfConnect) as redis:
            res = await redis.get(key)
            if res:
                return res

    async def get_all_keys(self) -> list[str]:
        async with aioredis.from_url(**self._redisConfConnect) as redis:
            all_keys = await redis.keys("*")
            return [key_b.decode() for key_b in all_keys]

    async def set(self, key: str, value: str | int | float | bool):
        async with aioredis.from_url(**self._redisConfConnect) as redis:
            await redis.set(key, value)
            await redis.expire(key, self.DEFAULT_EXPIRE)

    async def delete(self, key: str):
        async with aioredis.from_url(**self._redisConfConnect) as redis:
            await redis.delete(key)

    async def delete_startswith(self, startswith_key: str):
        async with aioredis.from_url(**self._redisConfConnect) as redis:
            keys_to_delete = await redis.keys(f"{startswith_key}*")
            if keys_to_delete:
                await redis.delete(*keys_to_delete)

    async def get_ttl(self, key: str) -> int:
        async with aioredis.from_url(**self._redisConfConnect) as redis:
            ttl = await redis.ttl(key)
            return ttl
