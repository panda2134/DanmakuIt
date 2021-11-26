from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

from app.config import app_config
from app.utils.room import generate_room_credentials, generate_passcode


class RoomCreation(BaseModel):
    name: str


class Room(RoomCreation):
    _id: Any # should be ObjectId from motor, but pydantic cannot handle that
    uid: str
    danmaku_enabled: bool = Field(True)
    room_id: str
    room_passcode: str
    creation_time: datetime
    remote_censor: bool = Field(True)
    keyword_blacklist: List[str] = Field([])
    wechat_token: str
    wechat_encrypted: bool = Field(False)
    wechat_encryption_key: Optional[str]

class RoomUpdate(BaseModel):
    name: Optional[str]
    danmaku_enabled: Optional[bool] = Field(True)
    room_passcode: Optional[str]
    remote_censor: Optional[bool] = Field(True)
    keyword_blacklist: Optional[List[str]] = Field([])
    wechat_token: Optional[str]
    wechat_encrypted: Optional[bool] = Field(False)
    wechat_encryption_key: Optional[str]


async def make_room(room, user):
    room_id, room_passcode = await generate_room_credentials()
    room = Room(uid=user.uid, name=room.name,
                room_id=room_id,
                room_passcode=room_passcode,
                creation_time=datetime.utcnow(),
                wechat_token=generate_passcode(app_config.room.wechat_token_length,
                                               room_id + app_config.wechat_passcode_salt))
    return room