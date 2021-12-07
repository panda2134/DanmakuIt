from typing import Optional
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

bg_queue: Optional[ArqRedis] = None
redis_settings = RedisSettings(host='redis')

async def get_bg_queue():
  global bg_queue
  if bg_queue is None:
    bg_queue = await create_pool(redis_settings)
  return bg_queue