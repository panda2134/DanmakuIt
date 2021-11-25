from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import app_config
from app.models.room import Room, RoomCreation, RoomUpdate
from app.db import db
from app.models.user import User
from app.utils import generate_passcode
from app.utils.jwt import get_current_user
from app.utils.room import generate_room_credentials

router = APIRouter(tags=['room'])


@router.post('/', response_model=Room)
async def create_room(room: RoomCreation, user: User = Depends(get_current_user)):
    room_id, room_passcode = await generate_room_credentials()
    room = Room(uid=user.uid, name=room.name,
                room_id=room_id,
                room_passcode=room_passcode,
                creation_time=datetime.utcnow(),
                wechat_token=generate_passcode(app_config.room.wechat_token_length))
    await db['room'].insert_one(room.dict())
    # TODO: push room data to pulsar
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
    # TODO: push room data to pulsar
    import devtools
    return await db['room'].find_one(q)


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