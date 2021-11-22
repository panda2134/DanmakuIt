import signal

import json
from hashlib import sha1
from xml.etree import ElementTree

from typing import Mapping, Optional

from cryptography.hazmat.primitives import serialization
import jwt

from aiohttp import web
import pulsar

with open('/private_key/private.key', 'rb') as f:
    private_key = serialization.load_der_private_key(f.read(), None)
# jwt's key can be cryptography key object or str(PEM/SSH or HMAC secret)
super_user_token = jwt.encode({'sub': 'super-user'}, private_key, algorithm='RS256', headers={'typ': None})

pulsar_client = pulsar.Client('pulsar://pulsar:6650', pulsar.AuthenticationToken(super_user_token))
raw_producer: Optional[pulsar.Producer] = None
state_update_producer: Optional[pulsar.Producer] = None

routes = web.RouteTableDef()

@routes.get('/token')
async def token_get(request: web.Request):
    return web.Response(text=super_user_token)

async def get_room_token(room: str):
    return 'placeholder'

@routes.post('/room/{room}/port')
async def room_port_post(request: web.Request):
    room = request.match_info['room']
    root = ElementTree.fromstring(await request.text())
    data: Mapping[str, str] = {el.tag: el.text for el in root}
    content = data.get('Content', '')
    sender = 'user_' + data.get('FromUserName', '')

    global raw_producer
    if raw_producer is None:
        raw_producer = pulsar_client.create_producer(
            'persistent://public/default/raw',
            block_if_queue_full=True,
            batching_enabled=True,
            batching_max_publish_delay_ms=10
        )

    def callback(res, msg_id): pass

    raw_producer.send_async(
        content=json.dumps(
            dict(
                content=content,
                sender=sender,
                room=room,
            ),
            ensure_ascii=False
        ).encode(),
        callback=callback
    )
    return web.Response(text='success')

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

@routes.post('/setting/{room}')
async def setting_post(request: web.Request):
    room = request.match_info['room']
    state_str = await request.text()
    global state_update_producer
    if state_update_producer is None:
        state_update_producer = pulsar_client.create_producer(
            'persistent://public/default/state',
            block_if_queue_full=True
        )
    def callback(res, msg_id): pass

    state_update_producer.send_async(
        content=json.dumps([room, 'replace', state_str]).encode(),
        callback=callback
    )
    return web.Response(text='success')
            

@routes.get('/debug/{room}')
async def debug_room(request: web.Request):
    room = request.match_info['room']
    reader = pulsar_client.create_reader(f'persistent://public/default/{room}', start_message_id=pulsar.MessageId.earliest)
    msgs = []
    while reader.has_message_available():
        # receive/read_next will block whole server if there is no message available
        msg = reader.read_next().properties()
        msgs.append(msg)
    
    return web.Response(text=str(msgs))

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

def atexit_function(*args):
    if raw_producer is not None:
        raw_producer.flush()
    pulsar_client.close()
    raise web.GracefulExit

signal.signal(signal.SIGTERM, atexit_function)
signal.signal(signal.SIGINT, atexit_function)

if __name__ == '__main__':
    web.run_app(app, port=8000)
