from datetime import datetime
from typing import Tuple
import random
import string

from app.utils import generate_passcode
from app.db import db
from app.config import app_config



async def generate_room_credentials() -> Tuple[str, str]:
    while True:
        number_part1 = int(datetime.utcnow().timestamp())
        number_part2 = random.randint(1, 1 << 5)
        room_id = (number_part1 << 5) | number_part2 # todo: better id generation to avoid enumerating
        if not await db['room'].find_one({ 'room_id': room_id }):
            break
    room_passcode = generate_passcode(app_config.room.room_passcode_length)
    return str(room_id), room_passcode
