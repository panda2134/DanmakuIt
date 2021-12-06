""" ARQ Background Task Worker.
"""

from app.bgtasks.wechat import *

class WorkerSettings:
  functions = [refresh_all_wechat_access_token,
               refresh_wechat_access_token_room]
