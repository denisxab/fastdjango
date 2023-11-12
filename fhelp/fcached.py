"""
Работа с Кешем
"""
import json
from typing import Any

from redis import Redis
from redis import asyncio as aioredis

from settings import REDIS_URL


class BaseCached:
    async def get_cached():
        """Получить объект взаимодействие с кешем, использовать в fastapi.Depends

        from fastapi import Depends
        from redis import Redis
        from .models import User


        @router_persons.get("/users/")
        def read_user_all(key:str, redis: Redis = Depends(get_cached)):
            res = await redis.get(key)
            return {"res": res}
        """

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
    """Кеш в оперативной памяти сервера

    Плюсы:
    - Самый быстрый кеш

    Минус:
    -  Кеш храниться на одном WebApp и не синхронизирован с другими WebApp
    """

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
        # Создаем список ключей, которые нужно удалить
        keys_to_delete = [key for key in self._data.keys() if key.startswith(key)]

        # Удаляем эти ключи из словаря
        for startswith_key in keys_to_delete:
            del self._data[startswith_key]


class RedisCached(BaseCached):
    """Кеш в Redis

    Плюсы:
    - Кеш храниться на внешнем сервере, и синхронизирован между WebApp

    Минус:
    -  Меленее чем RamServerCached
    """

    # По умолчанию значение храниться 3 минуты
    DEFAULT_EXPIRE = 60 * 3

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

    async def get_all_keys(self) -> list[str]:
        """Получить все ключи в Redis"""
        redis: Redis = aioredis.from_url(**self._redisConfConnect)
        all_keys = await redis.keys("*")
        return [key_b.decode() for key_b in all_keys]

    async def set(self, key: str, value: str | int | float | bool):
        redis: Redis = aioredis.from_url(**self._redisConfConnect)
        await redis.set(key, value)
        await redis.expire(key, self.DEFAULT_EXPIRE)

    async def delete(self, key: str):
        redis: Redis = aioredis.from_url(**self._redisConfConnect)
        await redis.delete(key)

    async def delete_startswith(self, startswith_key: str):
        redis: Redis = aioredis.from_url(**self._redisConfConnect)
        keys_to_delete = await redis.keys(f"{startswith_key}*")
        if keys_to_delete:
            await redis.delete(*keys_to_delete)

    async def get_ttl(self, key: str) -> int:
        """Получить TTL (время жизни) ключа в Redis"""
        redis: Redis = aioredis.from_url(**self._redisConfConnect)
        ttl = await redis.ttl(key)
        return ttl
