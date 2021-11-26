import string
import secrets

passcode_charset = set(string.digits + string.ascii_letters)
passcode_charset -= {'l', '1', 'I', '0', 'O'}


def generate_passcode(length: int) -> str:
    passcode = ''.join([secrets.choice(list(passcode_charset)) for _ in range(length)])
    return passcode
