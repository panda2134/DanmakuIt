import struct
import time
import string
import secrets
from typing import Tuple
from hashlib import sha256
from binascii import b2a_base64


def generate_room_id():
    h = sha256(struct.pack('f', time.time()))
    h.update(secrets.token_bytes(32))
    room_id = int.from_bytes(h.digest()[-4:], 'little')
    return str(room_id).ljust(10, '0')


def readable_sha256(binary: bytes, readable_char_table = bytes.maketrans(b'l1I0O+/=', b'LLLooXYZ')) -> str:
    return b2a_base64(sha256(binary).digest(), newline=False).translate(readable_char_table).decode()
    

