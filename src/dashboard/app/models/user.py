from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    username: str
    avatar: Optional[str]  # should be a DataURL, or a URL pointing to the avatar
    uid: str # wechat:<unionid>


