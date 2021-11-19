import json
from hashlib import sha1
from xml.etree import ElementTree

import signal

from typing import Mapping, Optional

from aiohttp import web
import pulsar
pulsar_client = pulsar.Client('pulsar://pulsar:6650')
producer: Optional[pulsar.Producer] = None

routes = web.RouteTableDef()

async def get_room_token(room: str):
    return 'placeholder'

@routes.get('/room/{room}/port')
async def room_port_get(request: web.Request):
    room = request.match_info['room']
    token = await get_room_token(room)

    query = request.query
    timestamp = query.get('timestamp', '')
    nonce = query.get('nonce', '')
    signature = query.get('signature', '')

    tmpArr = [token, timestamp, nonce]
    tmpArr.sort()
    hash = sha1()
    hash.update(''.join(tmpArr).encode('utf-8'))
    if (hash.hexdigest() == signature):
        echostr = query.get('echostr', '')
        return web.Response(text=echostr)
    
    return web.Response(text='Wrong signature!')

def send_raw_callback(res, msg_id):
    pass

@routes.post('/room/{room}/port')
async def room_port_post(request: web.Request):
    room = request.match_info['room']
    root = ElementTree.fromstring(await request.text())
    data: Mapping[str, str] = {el.tag: el.text for el in root}
    content = data.get('Content', '')
    sender = 'user_' + data.get('FromUserName', '')

    global producer
    if producer is None:
        producer = pulsar_client.create_producer('persistent://public/default/raw')

    producer.send_async(
        content=json.dumps(
            dict(
                content=content,
                sender=sender,
                room=room
            ),
            ensure_ascii=False
        ).encode(),
        callback=send_raw_callback
    )
    return web.Response(text='success')

@routes.get('/room/{room}')
async def debug_room(request: web.Request):
    room = request.match_info['room']
    reader = pulsar_client.create_reader(f'persistent://public/default/{room}', start_message_id=pulsar.MessageId.earliest)
    msgs = []
    while reader.has_message_available():
        # receive/read_next will block whole server if there is no message available
        msg: bytes = reader.read_next().data()
        msgs.append(msg.decode())
    
    return web.Response(text=str(len(msgs)))

@routes.get('/raw')
async def debug_raw(request: web.Request):
    reader = pulsar_client.create_reader('raw', start_message_id=pulsar.MessageId.earliest)
    msgs = []
    while reader.has_message_available():
        # receive/read_next will block whole server if there is no message available
        msg: bytes = reader.read_next().data()
        msgs.append(msg.decode())
    
    return web.Response(text=str(msgs))



app = web.Application()
app.add_routes(routes)

def atexit_function():
    if producer is not None:
        producer.flush()
    pulsar_client.close()

signal.signal(signal.SIGTERM, atexit_function)
signal.signal(signal.SIGINT, atexit_function)

if __name__ == '__main__':
    web.run_app(app, port=8000)
