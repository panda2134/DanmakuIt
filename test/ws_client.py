import json

import signal
from threading import Thread
from time import sleep

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


schema = 'ws'
domain = 'localhost:8000' # 'se-srv2.panda2134.site'

if __name__ == '__main__':
    token = requests.post(f'http://{domain}/room/3').text
    ws = websocket.WebSocketApp(
        f'{schema}://{domain}/websocket/consumer/persistent/public/default/3/sub?token={token}',
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