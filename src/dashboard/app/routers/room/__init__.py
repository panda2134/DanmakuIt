import secrets
from typing import Any, Callable, Coroutine, Sequence, List

import asyncio
from datetime import datetime
from arq.connections import ArqRedis

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from httpx import HTTPError

from app.bgtasks import get_bg_queue
from app.models.danmaku import DanmakuMessage

from app.models.room import Room, RoomNameModel, RoomUpdate, RoomIdModel, RoomQRCodeResponse, OnlineSubscription
from app.models.user import User
from app.utils.jwt import get_current_user
from app.utils.room import generate_room_id, readable_sha256, push_setting

from app.config import app_config
from pymongo import DESCENDING
from app.db import get_db
from app.http_client import http_client

router = APIRouter(tags=['room'])


async def rollback(rollback_op: Callable[[], Coroutine[Any, Any, bool]]):
    for i in range(app_config.max_rollback_retry):
        if await rollback_op():
            return
        await asyncio.sleep(1.5 ** i)
    # TODO: Log FATAL ERROR
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Rollback retry failed')


@router.post('/', response_model=Room)
async def create_room(room: RoomNameModel, user: User = Depends(get_current_user)):
    room_id = generate_room_id()
    resp = await http_client.post(f'{app_config.controller_url}/room/{room_id}')
    if not resp.is_success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Cannot create the room in controller. {resp.text}')

    pulsar_jwt = resp.text
    # -1 to skip paddings in base64
    wechat_token = readable_sha256(room_id.encode() +
                                   app_config.wechat_token_salt)[:app_config.room.wechat_token_length]
    room_passcode = readable_sha256(secrets.token_bytes(32))[:app_config.room.room_passcode_length]
    room = Room(uid=user.uid, name=room.name,
                room_id=room_id,
                creation_time=datetime.utcnow(),
                pulsar_jwt=pulsar_jwt,
                room_passcode=room_passcode,
                wechat_token=wechat_token)
    db = get_db()
    try:
        insert_result = await db['room'].insert_one(room.dict())
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Cannot create the room in database.')
    resp = await push_setting(http_client, room_id, room, mode='force')
    if not resp.is_success:
        async def rollback_op():
            delete_result = await db['room'].delete_one({'_id': insert_result.inserted_id})
            return bool(delete_result.deleted_count == 1)

        await rollback(rollback_op)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Cannot initialize setting the room in controller. {resp.status_code}')

    return room


@router.get('/', response_model=Sequence[Room], response_description="last 100 created rooms")
async def list_room(user: User = Depends(get_current_user)):
    room_docs = await get_db()['room'].find({'uid': user.uid}).sort('creation_time', DESCENDING).to_list(100)
    return room_docs


def room_with_auth(room_id: str, user: User = Depends(get_current_user)):
    """Authenticate the user, and then construct the query object for the given room.
    """
    return {'room_id': room_id, 'uid': user.uid}


@router.get('/{room_id}', response_model=Room)
async def get_room(room_query: dict = Depends(room_with_auth)):
    doc = await get_db()['room'].find_one(room_query)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    return doc


@router.patch('/{room_id}', response_model=Room, description="uid, room_id and creation_time cannot be altered")
async def modify_room(room: RoomUpdate, room_id: str, room_query: dict = Depends(room_with_auth),
                      bg_queue: ArqRedis = Depends(get_bg_queue)):
    db = get_db()
    update_dict = room.dict(exclude_unset=True)
    origin_room = await db['room'].find_one_and_update(room_query, {'$set': update_dict})
    if origin_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    updated_room = Room.parse_obj(dict(origin_room, **update_dict))
    # TODO: use setting version to ensure the consistency between database and pulsar
    resp = await push_setting(http_client, room_id, updated_room)
    if not resp.is_success:
        _id = origin_room['_id']

        async def rollback_op():
            replace_result = await db['room'].replace_one({'_id': _id}, origin_room)
            return bool(replace_result.modified_count == 1)

        await rollback(rollback_op)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Cannot modify setting the room in controller.')
    if room.wechat_appid is not None or room.wechat_appsecret is not None:  # appid or appsecret is updated
        await bg_queue.enqueue_job('refresh_wechat_access_token_room',
                                   updated_room.room_id, updated_room.wechat_appid, updated_room.wechat_appsecret)
    return updated_room


@router.delete('/{room_id}', response_model=RoomIdModel)
async def delete_room(room_id: str, room_query: dict = Depends(room_with_auth)):
    if not await get_db()['room'].count_documents(room_query, limit=1):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    
    resp = await http_client.delete(f'{app_config.controller_url}/room/{room_id}')
    if not resp.is_success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Cannot delete the room in controller. {resp.text}')

    retry = 0
    while (await get_db()['room'].delete_one(room_query)).deleted_count == 0:
        if (retry := retry + 1) > 5: # can we roll back?
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Cannot delete the room.')
        await asyncio.sleep(2.0)

    return {'room_id': room_id}


room_passcode_scheme = HTTPBearer()


@router.get('/{room_id}/client-login', response_model=Room,
            description='Set `room_passcode` in HTTP Bearer; `pulsar_jwt` is then used for pulsar connection')
async def client_login_room(room_id: str, passcode: HTTPAuthorizationCredentials = Depends(room_passcode_scheme)):
    doc = await get_db()['room'].find_one({'room_id': room_id})
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    room = Room.parse_obj(doc)

    # here, we use compare_digest to avoid timing attack.
    # please refer to https://docs.python.org/zh-cn/3/library/secrets.html#secrets.compare_digest
    # note that passcode has to be stored in plain text, since it shall be displayed on the frontend.

    if not secrets.compare_digest(room.room_passcode, passcode.credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid room passcode.')

    return room


# the unused local variable is for authentication purposes; do not remove it!
# noinspection PyUnusedLocal
@router.get('/{room_id}/qrcode', response_model=RoomQRCodeResponse,
            description='Set `room_passcode` in HTTP Bearer;' +
                        'This is provided for clients so that they can fetch the QR code without JWT.')
async def get_room_qrcode(room_id: str, passcode: HTTPAuthorizationCredentials = Depends(room_passcode_scheme)):
    doc = await get_db()['room'].find_one({'room_id': room_id})
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')

    # fetch QR Code from WeChat Official Account API
    room = Room.parse_obj(doc)
    if room.wechat_access_token is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='No WeChat access token.')
    try:
        res = await http_client.post(f'https://api.weixin.qq.com/cgi-bin/qrcode/create',
                                     json={'action_name': 'QR_STR_SCENE',
                                           'expire_seconds': 2592000,
                                           'action_info': {'scene': {'scene_str': room_id}}},
                                     params={'access_token': room.wechat_access_token})
        res.raise_for_status()
        return res.json()
    except HTTPError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Cannot get QR code from WeChat.')


@router.post('/{room_id}/fetch-subscribers', response_model=RoomIdModel,
             description='Fetch the user information of all subscribers.' +
                         'Returns room_id in JSON when the fetch process starts.')
async def fetch_subscribers_of_room(room_id: str, room_query: dict = Depends(room_with_auth)):
    if not await get_db()['room'].count_documents(room_query, limit=1):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    try:
        res = await http_client.post(f'{app_config.controller_url}/feed/{room_id}')
        res.raise_for_status()
        return {'room_id': room_id}
    except HTTPError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Cannot start fetching subscribers.')


@router.post('/{room_id}/danmaku-admin', response_model=DanmakuMessage,
             description='Send a danmaku message from admin. Sender in danmaku will always be overwritten to admin.')
async def danmaku_admin_send(room_id: str, room_query: dict = Depends(room_with_auth),
                         danmaku: DanmakuMessage = Body(...)):
    if not await get_db()['room'].count_documents(room_query, limit=1):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    try:
        res = await http_client.post(f'{app_config.controller_url}/danmaku-alter/{room_id}',
                                     json=danmaku.dict(), params={'type': 'send'})
        res.raise_for_status()
    except HTTPError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Cannot send admin danmaku.')
    return danmaku


@router.post('/{room_id}/danmaku-update', response_model=DanmakuMessage,
             description='Update a danmaku message.')
async def danmaku_update(room_id: str, room_query: dict = Depends(room_with_auth),
                         danmaku: DanmakuMessage = Body(...)):
    if not await get_db()['room'].count_documents(room_query, limit=1):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    try:
        res = await http_client.post(f'{app_config.controller_url}/danmaku-alter/{room_id}',
                                     json=danmaku.dict())
        res.raise_for_status()
    except HTTPError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Cannot update danmaku.')
    return danmaku


@router.get('/{room_id}/consumers', response_model=List[OnlineSubscription],
             description='Get the online consumers of a room.')
async def online_consumers(room_id: str, room_query: dict = Depends(room_with_auth)):
    if not await get_db()['room'].count_documents(room_query, limit=1):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    try:
        res = await http_client.get(f'{app_config.controller_url}/room/{room_id}/consumers')
        res.raise_for_status()
        response_json = res.json()  # {subscription_name: List[ConsumerDetail]}
        subscription_list: List[OnlineSubscription] = []
        for subscription_name, consumers in response_json.items():
            subscription_list.append(OnlineSubscription(
                subscription_name=subscription_name,
                consumers=consumers
            ))
        return subscription_list
    except HTTPError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Cannot get online consumers.')
