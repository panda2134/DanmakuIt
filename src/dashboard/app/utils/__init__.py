import string
import random

passcode_charset = set(string.digits + string.ascii_letters)
passcode_charset -= {'l', '1', 'I', '0', 'O'}


def generate_passcode(length: int) -> str:
    passcode = ''.join([random.choice(list(passcode_charset)) for i in range(length)])
    return passcode
