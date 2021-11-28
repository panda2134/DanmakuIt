from typing import Any, Callable, Coroutine, Sequence

import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.models.room import Room, RoomCreation, RoomUpdate, RoomDeletal
from app.models.user import User
from app.utils.jwt import get_current_user
from app.utils.room import generate_room_id, readable_sha256

from app.config import app_config
from pymongo import DESCENDING
from app.db import room_collection
from app.http_client import http_client


router = APIRouter(tags=['room'])

salt = b'place_holder'  # TODO: allow admin regenerate salt without restart sever


def notify_controller_on_update(room_id: str, room: Room):
    return http_client.post(f'{app_config.controller_url}/setting/{room_id}',
                            json=jsonable_encoder(room))

async def rollback(rollback_op: Callable[[], Coroutine[Any, Any, bool]]):
    for i in range(app_config.max_rollback_retry):
        if rollback_op():
            return
        await asyncio.sleep(1.5 ** i)
    # TODO: Log FATAL ERROR
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Rollback retry failed')


@router.post('/', response_model=Room)
async def create_room(room: RoomCreation, user: User = Depends(get_current_user)):
    room_id = generate_room_id()
    resp = await http_client.post(f'{app_config.controller_url}/room/{room_id}')
    if not resp.is_success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Cannot create the room in controller.')

    pulsar_token = resp.text
    room = Room(uid=user.uid, name=room.name,
                room_id=room_id,
                creation_time=datetime.utcnow(),
                pulsar_token=pulsar_token,
                wechat_token=readable_sha256(room_id.encode() + salt))
    try:
        insert_result = await room_collection.insert_one(room.dict())
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Cannot create the room in database.')
    resp = await notify_controller_on_update(room_id, room)
    if not resp.is_success:
        async def rollback_op():
            delete_result = await room_collection.delete_one({'_id': insert_result.inserted_id})
            return bool(delete_result.deleted_count == 1)
        await rollback(rollback_op)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Cannot initialize setting the room in controller.')
    
    return room


@router.get('/', response_model=Sequence[Room], response_description="last 100 created rooms")
async def list_room(user: User = Depends(get_current_user)):
    room_docs = await room_collection.find({'uid': user.uid}).sort('creation_time', DESCENDING).to_list(100)
    return room_docs


def room_query_from_id(room_id: str):
    return {'room_id': room_id}


@router.get('/{room_id}', response_model=Room)
async def get_room(room_query: dict = Depends(room_query_from_id)):
    doc = await room_collection.find_one(room_query)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    return doc


@router.patch('/{room_id}', response_model=Room, description="uid, room_id and creation_time cannot be altered")
async def modify_room(room: RoomUpdate, room_id: str, room_query: dict = Depends(room_query_from_id)):
    update_dict = room.dict(exclude_unset=True)
    origin_room = await room_collection.find_one_and_update(room_query, {'$set': update_dict})
    if origin_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    updated_room = Room.parse_obj(dict(origin_room, **update_dict))
    # TODO: use setting version to ensure the consistency between database and pulsar
    resp = await notify_controller_on_update(room_id, updated_room)
    if not resp.is_success:
        _id = origin_room['_id']
        async def rollback_op():
            replace_result = await room_collection.replace_one({'_id': _id}, origin_room)
            return bool(replace_result.modified_count == 1)
        await rollback(rollback_op)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Cannot modify setting the room in controller.')
    return updated_room


@router.delete('/{room_id}', response_model=RoomDeletal)
async def delete_room(room_id: str, room_query: dict = Depends(room_query_from_id)):
    if not await room_collection.count_documents(room_query, limit=1):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    res = await room_collection.delete_one(room_query)
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Cannot delete the room.')

    # TODO: push deletion of room to pulsar
    return {'room_id': room_id}
