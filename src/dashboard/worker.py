""" ARQ Background Task Worker.
"""

import logging
from logging import getLogger
from typing import Mapping, Any
import asyncio

from arq import Retry, ArqRedis

import httpx
from pydantic import BaseModel
from app.bgtasks import redis_settings
from app.db import get_db

from app.config import app_config
from app.models.room import Room
from app.utils.room import push_setting


logger = getLogger('bgtasks').getChild('wechat')
logger.setLevel(logging.INFO)


class WeChatAccessTokenReply(BaseModel):
    access_token: str
    expires_in: int

async def resume_controller(ctx: Mapping[str, Any]):
    async for room_obj in get_db()['room'].find():
        room = Room.parse_obj(room_obj)
        resp = await push_setting(ctx['http_client'], room.room_id, room, mode='resume')
        while not resp.is_success:
            await asyncio.sleep(2.0)
            resp = await push_setting(ctx['http_client'], room.room_id, room, mode='resume')

async def refresh_wechat_access_token_all(ctx: Mapping[str, Any]):
    bg_queue: ArqRedis = ctx['redis']
    async for room_obj in get_db()['room'].find():
        room = Room.parse_obj(room_obj)
        if room.wechat_appid is None or room.wechat_appsecret is None:
            logger.info(f'Room {room.room_id} has no WeChat appid / appsecret, skipped')
            continue  # skip this room
        logger.info(f'Room {room.room_id} queued for access_token refresh')
        await bg_queue.enqueue_job('refresh_wechat_access_token_room', room.room_id, room.wechat_appid, room.wechat_appsecret)


async def refresh_wechat_access_token_room(ctx: Mapping[str, Any], room_id, wechat_appid, wechat_appsecret):
    room = await get_db()['room'].find_one({'room_id': room_id})

    # if room is deleted or updated, stop recursion
    if room is None:
        return
    if room.get('wechat_appid') != wechat_appid:
        return
    if room.get('wechat_appsecret') != wechat_appsecret:
        return
    
    http_client: httpx.AsyncClient = ctx['http_client']
    resp = await http_client.get(
        'https://api.weixin.qq.com/cgi-bin/token',
        params={
            'grant_type': 'client_credential',
            'appid': wechat_appid,
            'secret': wechat_appsecret
        })
    try:
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise KeyError(f'HTTP status error in access_token request for room {room_id}: {e}')
    resp_obj: Mapping[str, Any] = resp.json()
    if 'errcode' in resp_obj:
        if resp_obj['errcode'] == -1:  # retry later
            raise Retry(defer=app_config.room.wechat_retry_secs)
        raise KeyError(f'Error in access_token request for room {room_id}: {resp_obj}')

    reply = WeChatAccessTokenReply.parse_obj(resp_obj)
    await http_client.put(f'{app_config.controller_url}/token/{room_id}', content=reply.access_token)
    logger.info(f'Room {room_id} access_token pushed to controller')

    bg_queue: ArqRedis = ctx['redis']
    async def deferred_recursion():
        expir = float(reply.expires_in)
        await asyncio.sleep(max(expir / 2, expir - 1e3))
        await bg_queue.enqueue_job('refresh_wechat_access_token_room', room_id, wechat_appid, wechat_appsecret)
    asyncio.create_task(deferred_recursion())

async def startup(ctx):
    ctx['http_client'] = httpx.AsyncClient()
    bg_queue: ArqRedis = ctx['redis']
    await bg_queue.enqueue_job('refresh_wechat_access_token_all')
    await bg_queue.enqueue_job('resume_controller')

async def shutdown(ctx):
    http_client: httpx.AsyncClient = ctx['http_client']
    await http_client.aclose()

class WorkerSettings:
    redis_settings = redis_settings
    functions = [refresh_wechat_access_token_all, refresh_wechat_access_token_room]
    on_startup = startup
    on_shutdown = shutdown
