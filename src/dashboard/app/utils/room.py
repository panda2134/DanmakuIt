import struct
import time
from typing import Tuple
import secrets
from hashlib import sha256

from app.utils import generate_passcode
from app.db import db
from app.config import app_config


def generate_room_id():
    h = sha256()
    h.update(struct.pack('f', time.time()))
    h.update(secrets.token_bytes(32))
    return int.from_bytes(h.digest()[-4:], 'little')


async def generate_room_credentials() -> Tuple[str, str]:
    while True:
        room_id = generate_room_id()
        if not await db['room'].find_one({'room_id': room_id}):
            break
    room_passcode = generate_passcode(app_config.room.room_passcode_length)
    return str(room_id).ljust(10, '0'), room_passcode
