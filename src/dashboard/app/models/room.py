from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class RoomNameModel(BaseModel):
    name: str


class RoomIdModel(BaseModel):
    room_id: str


class RoomQRCodeResponse(BaseModel):
    ticket: str
    expire_seconds: int
    url: str


class Room(RoomNameModel):
    _id: Any # should be ObjectId from motor, but pydantic cannot handle that
    uid: str
    danmaku_enabled: bool = Field(True)
    room_id: str
    room_passcode: str
    creation_time: datetime
    remote_censor: bool = Field(True)
    keyword_blacklist: List[str] = Field([])
    pulsar_jwt: str
    wechat_token: str
    wechat_encrypted: bool = Field(False)
    wechat_encryption_key: Optional[str]
    wechat_appid: Optional[str]
    wechat_appsecret: Optional[str]
    wechat_access_token: Optional[str]  # for QR code generation
    user_danmaku_colors: Optional[List[str]]


class RoomUpdate(BaseModel):
    name: Optional[str]
    danmaku_enabled: Optional[bool] = Field(True)
    remote_censor: Optional[bool] = Field(True)
    keyword_blacklist: Optional[List[str]] = Field([])
    wechat_token: Optional[str]
    wechat_encrypted: Optional[bool] = Field(False)
    wechat_encryption_key: Optional[str]
    wechat_appid: Optional[str]
    wechat_appsecret: Optional[str]
    user_danmaku_colors: Optional[List[str]]