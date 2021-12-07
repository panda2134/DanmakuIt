from typing import Optional
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

redis_settings = RedisSettings(host='redis')

def _():
  bg_queue: Optional[ArqRedis] = None
  async def get_bg_queue():
    nonlocal bg_queue
    if bg_queue is None:
      bg_queue = await create_pool(redis_settings)
    return bg_queue
  return get_bg_queue
get_bg_queue = _()
_ = None