from typing import Optional, TYPE_CHECKING

import aioredis
from aioredis import Redis

from store.base import BaseAccessor

if TYPE_CHECKING:
    from main import Application


class RedisAccessor(BaseAccessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_url = "redis://redis:6379/1"
        self.redis: Optional["Redis"] = None

    async def connect(self, app: "Application"):
        self.redis = await aioredis.from_url(self.redis_url)

    async def disconnect(self, app: "Application"):
        await self.redis.close()

    async def get_sid(self, profile_id: str) -> str:
        sid = await self.redis.get(profile_id)
        return sid

    async def set_sid(self, sid: str, profile_id: str) -> None:
        await self.redis.set(profile_id, sid)

    async def delete_sid(self, profile_id: str) -> None:
        await self.redis.delete(profile_id)

    async def many_get(self, profiles_id: list[str]) -> list[str]:
        sids = await self.redis.mget(profiles_id)
        return sids
