from typing import Optional, Sequence, Callable

import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from httpx import HTTPError

from app.models.room import Room, RoomCreation, RoomUpdate, RoomDeletal
from app.models.user import User
from app.utils.jwt import get_current_user
from app.utils.room import generate_room_id, readable_sha256

from app.config import app_config
from app.db import *
from pymongo import DESCENDING
from app.http_client import http_client


router = APIRouter(tags=['room'])

salt = b'place_holder'  # TODO: allow admin regenerate salt without restart sever


async def notify_pulsar(fn: Callable):
    if app_config.pulsar_enabled:
        try:
            await fn()
        except HTTPError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Failed to notify pulsar.')


async def notify_pulsar_on_creation(room_id: str):
    async def creation_fn():
        create_res = await http_client.post(f'{app_config.controller_url}/room/{room_id}')
        create_res.raise_for_status()
    await notify_pulsar(creation_fn)


async def notify_pulsar_on_update(room_id: str, room: Room):
    async def update_fn():
        update_res = await http_client.post(f'{app_config.controller_url}/setting/{room_id}',
                                            json=jsonable_encoder(room))
        update_res.raise_for_status()
    await notify_pulsar(update_fn)


@router.post('/', response_model=Room)
async def create_room(room: RoomCreation, user: User = Depends(get_current_user)):
    room_id = generate_room_id()

    room = Room(uid=user.uid, name=room.name,
                room_id=room_id,
                creation_time=datetime.utcnow(),
                wechat_token=readable_sha256(room_id.encode() + salt))
    async with await db_client.start_session() as s:
        async with s.start_transaction():
            await room_collection.insert_one(room.dict())
            await notify_pulsar_on_creation(room_id)
            await notify_pulsar_on_update(room_id, room)

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
    async with await db_client.start_session() as s:
        async with s.start_transaction():
            updated_room = await room_collection.find_one_and_update(room_query, {'$set': room.dict(exclude_unset=True)},
                                                                     return_document=ReturnDocument.AFTER)
            if updated_room is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
            updated_room = Room.parse_obj(updated_room)
            await notify_pulsar_on_update(room_id, updated_room)
            return updated_room


@router.delete('/{room_id}', response_model=RoomDeletal)
async def delete_room(room_id: str, room_query: dict = Depends(room_query_from_id)):
    res = await room_collection.delete_one(room_query)
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Cannot delete the room.')

    # TODO: push deletion of room to pulsar
    return {'room_id': room_id}
