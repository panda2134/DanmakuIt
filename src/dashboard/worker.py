""" ARQ Background Task Worker.
"""

from app.bgtasks import redis_settings
from app.bgtasks.wechat import *
from arq import cron

class WorkerSettings:
  redis_settings = redis_settings
  functions = [refresh_all_wechat_access_token,
               refresh_wechat_access_token_room]
  cron_jobs = [
    cron(refresh_all_wechat_access_token, hour=set(range(24)), minute=0)
  ]
