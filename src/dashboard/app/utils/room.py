import struct
import time
import secrets
from hashlib import sha256
from binascii import b2a_base64

from httpx import AsyncClient

from app.config import app_config
from app.models.room import Room


def generate_room_id():
    h = sha256(struct.pack('f', time.time()))
    h.update(secrets.token_bytes(32))
    room_id = int.from_bytes(h.digest()[-4:], 'little')
    return str(room_id).ljust(10, '0')


def readable_sha256(binary: bytes, readable_char_table=bytes.maketrans(b'l1I0O+/=', b'LLLooXYZ')) -> str:
    return b2a_base64(sha256(binary).digest(), newline=False).translate(readable_char_table).decode()


def push_setting(http_client: AsyncClient, room_id: str, room: Room, mode: str = None):
    return http_client.put(f'{app_config.controller_url}/setting/{room_id}',
                           json=room.dict(include={'danmaku_enabled', 'remote_censor', 'keyword_blacklist'}),
                           params={'mode': mode} if mode else None
                           )
