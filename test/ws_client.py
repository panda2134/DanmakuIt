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

ws = websocket.WebSocketApp(
    'ws://localhost:8080/ws/v2/consumer/persistent/public/default/3/testsub',
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)


ws_thread = Thread(target=ws.run_forever, daemon=True)

def atexit(*args):
    ws.close()
    ws_thread.join()
    exit()

signal.signal(signal.SIGINT, atexit)

ws_thread.start()

while True:
    sleep(1)