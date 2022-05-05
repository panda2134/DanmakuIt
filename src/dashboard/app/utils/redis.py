"""
Local cache for tokens, etc.

"""
from app.utils import async_cache, sync_cache
import aioredis


@async_cache
async def get_redis():
    return await aioredis.create_redis_pool('redis://redis')
