from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.config import app_config
from app.models.room import Room, RoomCreation, RoomUpdate, make_room
from app.db import db
from app.models.user import User
from app.utils.jwt import get_current_user

router = APIRouter(tags=['room'])


@router.post('/', response_model=Room)
async def create_room(room: RoomCreation, user: User = Depends(get_current_user)):
    room = await make_room(room, user)
    await db['room'].insert_one(room.dict())

    if not app_config.debug:
        try:
            with httpx.AsyncClient() as client:
                client: httpx.AsyncClient
                create_res = await client.post(app_config.controller_url + f'/room/{room.room_id}')
                create_res.raise_for_status()
                update_res = await client.post(app_config.controller_url + f'/setting/{room.room_id}',
                                               json=jsonable_encoder(room))
                update_res.raise_for_status()
        except httpx.HTTPError:
            await db['room'].delete_many(room.dict()) # rollback
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Failed to notify pulsar on room creation.')

    return room


@router.get('/', response_model=List[Room], response_description="last 100 created rooms")
async def list_room(user: User = Depends(get_current_user)):
    room_docs = await db['room'].find({'uid': user.uid}).sort('creation_time', -1).to_list(100)
    return room_docs


def get_room_query_from_room_id(room_id: str, user: User = Depends(get_current_user)):
    return {'room_id': room_id, 'uid': user.uid}


@router.get('/{room_id}', response_model=Room)
async def get_room(q: dict = Depends(get_room_query_from_room_id)):
    doc = await db['room'].find_one(q)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    return doc


@router.patch('/{room_id}', response_model=Room, description="uid, room_id and creation_time cannot be altered")
async def modify_room(room: RoomUpdate, q: dict = Depends(get_room_query_from_room_id)):
    update_data = room.dict(exclude_unset=True)
    res = await db['room'].update_one(q, {'$set': update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    room = Room.parse_obj(db['room'].find_one(q))

    if not app_config.debug:
        try:
            with httpx.AsyncClient() as client:
                client: httpx.AsyncClient
                update_res = await client.post(app_config.controller_url + f'/setting/{room.room_id}',
                                               json=jsonable_encoder(room))
                update_res.raise_for_status()
        except httpx.HTTPError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Failed to notify pulsar on room update.')
    return room


@router.delete('/{room_id}', response_model=Room)
async def delete_room(q: dict = Depends(get_room_query_from_room_id)):
    to_delete = await db['room'].find_one(q)
    if not to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such room.')
    res = await db['room'].delete_many(q)
    if not res.deleted_count:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Cannot delete the room.')
    # TODO: push deletion of room to pulsar
    return to_delete
