import signal

import json
from hashlib import sha1
from xml.etree import ElementTree

from typing import Mapping, Optional, Union

from cryptography.hazmat.primitives import serialization
import jwt

from aiohttp import web, ClientSession
import pulsar

with open('/private_key/private.key', 'rb') as f:
    private_key = serialization.load_der_private_key(f.read(), None)
# jwt's key can be cryptography key object or str(PEM/SSH or HMAC secret)
super_user_token = jwt.encode({'sub': 'super-user'}, private_key, algorithm='RS256', headers={'typ': None})
super_user_headers = {'Authorization': f'Bearer {super_user_token}'}

pulsar_client = pulsar.Client('pulsar://pulsar:6650', pulsar.AuthenticationToken(super_user_token))
raw_producer: Optional[pulsar.Producer] = None
state_update_producer: Optional[pulsar.Producer] = None

routes = web.RouteTableDef()

@routes.post('/room/{room}') # creat room
async def room_post(request: web.Request):
    room = request.match_info['room']
    async with ClientSession() as session:
        async with session.put(f'http://pulsar:8080/admin/v2/persistent/public/default/{room}', headers=super_user_headers) as resp:
            if resp.status not in {204, 409}:
                return web.Response(text=f'create topic error: {resp.status}')
        async with session.post(f'http://pulsar:8080/admin/v2/persistent/public/default/{room}/permissions/display_{room}', json=['consume'], headers=super_user_headers) as resp:
            if resp.status != 204:
                return web.Response(text=f'grant permission error: {resp.status}')
    token = jwt.encode({'sub': f'display_{room}'}, private_key, algorithm='RS256', headers={'typ': None})
    return web.Response(text=f'token:{token}')

async def get_room_token(room: str):
    return 'placeholder'

@routes.post('/room/{room}/port') # wechat send danmaku
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

@routes.get('/room/{room}/port') # wechat access
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

@routes.post('/setting/{room}') # replace room setting
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

@routes.get('/setting/{room}') # get room setting
async def setting_post(request: web.Request):
    room = request.match_info['room']
    async with ClientSession() as session:
        async with session.get(f'http://pulsar:8080/admin/v3/functions/public/default/tagger/state/{room}', headers=super_user_headers) as resp:
            obj: Mapping[str, Union[str,int]] = await resp.json()
            return web.Response(text=obj['stringValue'])

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
