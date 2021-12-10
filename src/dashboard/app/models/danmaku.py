from pydantic import BaseModel


class DanmakuMessage(BaseModel):
    color: str
    content: str
    id: str
    permission: str
    pos: str
    sender: str
    size: str
