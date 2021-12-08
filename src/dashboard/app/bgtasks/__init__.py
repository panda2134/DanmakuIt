from arq import create_pool
from arq.connections import RedisSettings

from app.utils import async_cache

redis_settings = RedisSettings(host='redis')

@async_cache
async def get_bg_queue():
    return await create_pool(redis_settings)