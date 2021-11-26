from typing import Optional, Sequence

import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from httpx import HTTPError

from app.models.room import Room, RoomCreation, RoomUpdate
from app.models.user import User
from app.utils.jwt import get_current_user
from app.utils.room import generate_room_id, readable_sha256

from app.config import app_config
from app.db import room_collection, DESCENDING, ReturnDocument
from app.http_client import http_client


router = APIRouter(tags=['room'])

salt = b'place_holder'  # TODO: allow admin regenerate salt without restart sever

rooms_id_cache: Optional[set] = None


@router.post('/', response_model=Room)
async def create_room(room: RoomCreation, user: User = Depends(get_current_user)):
    global rooms_id_cache
    if rooms_id_cache is None:
        rooms_id_cache = {doc['room_id'] for doc in await room_collection.find(projection=['room_id']).to_list()}

    while True:
        room_id = generate_room_id()
        if room_id not in rooms_id_cache:
            break
        await asyncio.sleep(0.2)

    room = Room(uid=user.uid, name=room.name,
                room_id=room_id,
                creation_time=datetime.utcnow(),
                wechat_token=readable_sha256(room_id.encode() + salt))
    if not app_config.debug:
        try:
            create_res = await http_client.post(f'{app_config.controller_url}/room/{room_id}')
            create_res.raise_for_status()
            update_res = await http_client.post(f'{app_config.controller_url}/setting/{room_id}',
                                                json=jsonable_encoder(room))
            update_res.raise_for_status()
        except HTTPError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Failed to notify pulsar on room creation.')
    await room_collection.insert_one(room.dict())
    rooms_id_cache.add(room_id)
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
    if room_id not in rooms_id_cache:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')

    updated_room = await room_collection.find_one_and_update(room_query, {'$set': room.dict(exclude_unset=True)}, return_document=ReturnDocument.AFTER)
    if updated_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cannot modify the room.')
    updated_room = Room.parse_obj(updated_room)
    if not app_config.debug:
        try:
            create_res = await http_client.post(f'{app_config.controller_url}/room/{room_id}')
            create_res.raise_for_status()
            update_res = await http_client.post(f'{app_config.controller_url}/setting/{room_id}',
                                                json=jsonable_encoder(updated_room))
            update_res.raise_for_status()
        except HTTPError:
            # TODO: roll back
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Failed to notify pulsar on room creation.')
    return updated_room


@router.delete('/{room_id}', response_model=Room)
async def delete_room(room_id: str, room_query: dict = Depends(room_query_from_id)):
    if room_id not in rooms_id_cache:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    res = await room_collection.delete_one(room_query)
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Cannot delete the room.')
    rooms_id_cache.remove(room_id)
    # TODO: push deletion of room to pulsar
    return room_id
