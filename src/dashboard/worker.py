""" ARQ Background Task Worker.
"""

import asyncio
import datetime
import logging
import os
from logging import getLogger
from typing import Mapping, Any

import httpx
from arq import Retry, ArqRedis
from pydantic import BaseModel
from weixin import WXAPPAPI

from app.bgtasks import redis_settings
from app.config import app_config
from app.db import get_db
from app.models.room import Room
from app.utils.mpsdk import mpsdk
from app.utils.room import push_setting
from app.utils.redis import get_redis

logger = getLogger('bgtasks').getChild('wechat')
logger.setLevel(logging.INFO)


class WeChatAccessTokenReply(BaseModel):
    access_token: str
    expires_in: int


async def resume_controller(ctx: Mapping[str, Any]):
    async for room_obj in get_db()['room'].find():
        room = Room.parse_obj(room_obj)
        while True:
            try:
                (await push_setting(ctx['http_client'], room.room_id, room, mode='resume')).raise_for_status()
                break
            except:
                await asyncio.sleep(5.0)


async def refresh_wechat_mp_access_token(ctx: Mapping[str, Any]):
    bg_queue: ArqRedis = ctx['redis']
    reply: Mapping[str, Any] = dict()
    try:
        reply = mpsdk.client_credential_for_access_token()
        logger.info('wechat-mp token: %s', reply)
        redis = await get_redis()
        await redis.set('mp_access_token', str(reply['access_token']).encode('utf8'),
                        expire=int(reply['expires_in']))
    except Exception as e:
        logger.warning('WeChat MiniProgram access_token update failed: %s', e)

    expire = float(reply['expires_in'])
    defer_secs = max(expire / 2, expire - 1e3)
    await bg_queue.enqueue_job('refresh_wechat_mp_access_token', _defer_by=datetime.timedelta(seconds=defer_secs))


async def refresh_wechat_access_token_all(ctx: Mapping[str, Any]):
    bg_queue: ArqRedis = ctx['redis']
    async for room_obj in get_db()['room'].find():
        room = Room.parse_obj(room_obj)
        if room.wechat_appid is None or room.wechat_appsecret is None:
            logger.info(f'Room {room.room_id} has no WeChat appid / appsecret, skipped')
            continue  # skip this room
        logger.info(f'Room {room.room_id} queued for access_token refresh')
        await bg_queue.enqueue_job('refresh_wechat_access_token_room', room.room_id, room.wechat_appid,
                                   room.wechat_appsecret)


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
    # store for QR code generation
    await get_db()['room'].update_one({'room_id': room_id}, {'$set': {'wechat_access_token': reply.access_token}})
    while True:
        try:
            (await http_client.put(f'{app_config.controller_url}/token/{room_id}', content=reply.access_token)).raise_for_status()
            break
        except:
            await asyncio.sleep(5.0)
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
    await bg_queue.enqueue_job('refresh_wechat_mp_access_token')


async def shutdown(ctx):
    http_client: httpx.AsyncClient = ctx['http_client']
    await http_client.aclose()


class WorkerSettings:
    redis_settings = redis_settings
    functions = [resume_controller, refresh_wechat_access_token_all,
                 refresh_wechat_access_token_room, refresh_wechat_mp_access_token]
    on_startup = startup
    on_shutdown = shutdown
