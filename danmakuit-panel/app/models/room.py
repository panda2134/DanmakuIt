from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RoomCreation(BaseModel):
    name: str


class Room(RoomCreation):
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
