import json

import signal
from threading import Thread
from time import sleep

from conf import room_id, room_passcode

import websocket
import requests


def on_message(ws: websocket.WebSocketApp, message: str):
    print(message)
    if message == '':
        ws.close()
        return
    msg = json.loads(message)
    print(msg['payload'])
    print(msg['properties'])
    ws.send(json.dumps({'messageId': msg['messageId']}))
    

def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### close ###")


def on_open(ws):
    print("### open ###")

# https://stackoverflow.com/questions/29931671/making-an-api-call-in-python-with-an-api-that-requires-a-bearer-token
class HTTPBearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


schema = 'wss'
domain = 'danmakuit.panda2134.site' # 'localhost:8000' # 'se-srv2.panda2134.site'


if __name__ == '__main__':
    response = requests.get(f'https://{domain}/api/v1/room/{room_id}/client-login', auth=HTTPBearerAuth(room_passcode)).json()
    print('Response from client_login:', response)
    ws = websocket.WebSocketApp(
        f'{schema}://{domain}/websocket/reader/persistent/public/default/user_{room_id}?messageId=earliest&token={response["pulsar_jwt"]}',
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )


    ws_thread = Thread(target=ws.run_forever)

    def atexit(*args):
        ws.close()
        ws_thread.join()
        exit()

    signal.signal(signal.SIGINT, atexit)
    signal.signal(signal.SIGTERM, atexit)

    ws_thread.start()

    while ws_thread.is_alive():
        sleep(1)
