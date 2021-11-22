import json

import signal
from threading import Thread
from time import sleep

import websocket


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

with open('../token/super_user') as f:
    token = f.read()

domain = 'ws://localhost:8000' # 'wss://se-srv2.panda2134.site'

ws = websocket.WebSocketApp(
    f'{domain}/websocket/consumer/persistent/public/default/3/sub?token={token}',
    # header={'Authorization': 'Bearer ' + token},
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