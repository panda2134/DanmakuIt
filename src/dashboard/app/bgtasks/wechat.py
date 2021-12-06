import httpx
from pydantic.main import BaseModel
from app.bgtasks import get_bg_queue
from app.db import get_db, MongoCollectionInterface
from app.models.room import Room, RoomUpdate
from app.http_client import http_client

class WeChatAccessTokenReply(BaseModel):
  access_token: str
  expires_in: int

async def refresh_all_wechat_access_token():
  db: MongoCollectionInterface = (await get_db())['room']
  bg_queue = await get_bg_queue()
  async for room_obj in db.find():
    room = Room.parse_obj(room_obj)
    if room.wechat_appid is None or room.wechat_appsecret is None:
      continue  # skip this room
    bg_queue.enqueue_job('refresh_wechat_access_token_room', room)

async def refresh_wechat_access_token_room(room: Room):
  db: MongoCollectionInterface = (await get_db())['room']
  resp = await http_client.get(
    'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential',
    params={
      'appid': room.wechat_appid,
      'appsecret': room.wechat_appsecret
  })
  resp.raise_for_status()
  if resp.json().get('errcode') is not None:
    raise KeyError(f'No response in access_token request for room {room.room_id}: {resp.json()}')
  reply: WeChatAccessTokenReply = resp.json()
  await db.update_one({ 'room_id': room.room_id }, 
                RoomUpdate.parse_obj({ 'wechat_access_token': reply.access_token }))
