from logging import getLogger
import httpx
from pydantic.main import BaseModel
from app.bgtasks import get_bg_queue
from app.db import get_db, MongoCollectionInterface
from app.models.room import Room, RoomUpdate
from app.http_client import http_client
from app.config import app_config
from arq import Retry


logger = getLogger('bgtasks').getChild('wechat')


class WeChatAccessTokenReply(BaseModel):
  access_token: str
  expires_in: int

async def refresh_all_wechat_access_token():
  db: MongoCollectionInterface = (await get_db())['room']
  bg_queue = await get_bg_queue()
  async for room_obj in db.find():
    room = Room.parse_obj(room_obj)
    if room.wechat_appid is None or room.wechat_appsecret is None:
      logger.info(f'Room {room.room_id} has no WeChat appid / appsecret, skipped')
      continue  # skip this room
    logger.info(f'Room {room.room_id} queued for access_token refresh')
    bg_queue.enqueue_job('refresh_wechat_access_token_room', room)

async def refresh_wechat_access_token_room(room: Room):
  db: MongoCollectionInterface = (await get_db())['room']
  resp = await http_client.get(
    'https://api.weixin.qq.com/cgi-bin/token',
    params={
      'grant_type': 'client_credential',
      'appid': room.wechat_appid,
      'appsecret': room.wechat_appsecret
  })
  try:
    resp.raise_for_status()
  except httpx.HTTPError as e:
    raise KeyError('HTTP status error in access_token request'
                  + f' for room {room.room_id}: {e}')
  resp_obj = resp.json()
  if resp_obj.get('errcode') is not None:
    if resp_obj['errcode'] == -1:  # retry later
      raise Retry(defer=app_config.room.wechat_retry_secs)
    else:
      raise KeyError('Error in access_token request for room '
                    + f'{room.room_id}: {resp_obj}')
  reply = WeChatAccessTokenReply.parse_obj(resp_obj)
  await db.update_one({ 'room_id': room.room_id }, 
    RoomUpdate.parse_obj({ 'wechat_access_token': reply.access_token }))
