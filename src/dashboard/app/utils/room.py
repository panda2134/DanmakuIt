import struct
import time
import string
import secrets
from typing import Tuple
from hashlib import sha256
from binascii import b2a_base64
from app.db import db
from app.config import app_config


passcode_trans = str.maketrans('l1I0O+/=', 'LLLooXYZ')


def generate_room_id():
    h = sha256(struct.pack('f', time.time()))
    h.update(secrets.token_bytes(32))
    room_id = int.from_bytes(h.digest()[-4:], 'little')
    return str(room_id).ljust(10, '0')


def generate_passcode(length: int, from_str: str) -> str:
    h = sha256(bytes(from_str, 'ascii'))
    passcode = b2a_base64(h.digest()).decode('ascii')
    passcode = passcode.translate(passcode_trans)
    return passcode[-length-5:-5]  # strip \n and padding


async def generate_room_credentials() -> Tuple[str, str]:
    while True:
        room_id = generate_room_id()
        if not await db['room'].find_one({'room_id': room_id}):
            break
    room_passcode = generate_passcode(app_config.room.room_passcode_length, room_id + app_config.room_passcode_salt)
    return room_id, room_passcode
