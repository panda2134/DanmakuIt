import asyncio

from hashlib import sha1, sha256
from binascii import b2a_base64
import json
from xml.etree import ElementTree
from time import time
import os

from typing import Mapping, MutableMapping, MutableSet, Optional

from cryptography.hazmat.primitives import serialization
import jwt

import aioredis
from httpx import AsyncClient
from sanic import Sanic, Request, text
import pulsar

with open('/private_key/private.key', 'rb') as f:
    private_key = serialization.load_der_private_key(f.read(), None)
# jwt's key can be cryptography key object or str(PEM/SSH or HMAC secret)
super_user_token = jwt.encode({'sub': 'super-user'}, private_key, algorithm='RS256', headers={'typ': None})

httpClient = AsyncClient(headers={'Authorization': f'Bearer {super_user_token}'})
pulsar_client = pulsar.Client('pulsar://pulsar:6650', pulsar.AuthenticationToken(super_user_token))
raw_producer: Optional[pulsar.Producer] = None
state_update_producer: Optional[pulsar.Producer] = None
user_producers: MutableMapping[str, pulsar.Producer] = {}

redis: aioredis.Redis = aioredis.from_url('redis://redis:6379/0', encoding="utf-8", decode_responses=True)
token_channel = redis.pubsub()
token_cache: MutableMapping[str, str] = {}
user_channel = redis.pubsub()
user_cache: MutableMapping[str, MutableSet] = {}

app = Sanic('Controller')

def get_raw_producer():
    global raw_producer
    if raw_producer is None:
        raw_producer = pulsar_client.create_producer(
            'persistent://public/default/raw',
            block_if_queue_full=True,
            batching_enabled=True,
            batching_max_publish_delay_ms=10
        )
    return raw_producer

def get_state_update_producer():
    global state_update_producer
    if state_update_producer is None:
        state_update_producer = pulsar_client.create_producer(
            'persistent://public/default/state',
            block_if_queue_full=True
        )
    return state_update_producer

def get_user_producer(room: str):
    if room not in user_producers:
        user_producers[room] = pulsar_client.create_producer(
            f'persistent://public/default/user_{room}',
            block_if_queue_full=True
        )
    return user_producers[room]

@app.before_server_start
async def setup(*args, **kwargs):
    await token_channel.subscribe('access_token')

    async def sync_token_cache():
        async for message in token_channel.listen():
            data: str = message['data']
            key, value = data.split(':')
            token_cache[key] = value
    asyncio.create_task(sync_token_cache())
    await user_channel.subscribe('room_user')
    # TODO: read from pulsar to recover data

    async def sync_user_cache():
        async for message in user_channel.listen():
            data: str = message['data']
            key, value = data.split(':')
            if key not in user_cache:
                user_cache[key] = set()
            user_cache[key].add(value)
    asyncio.create_task(sync_user_cache())


@app.after_server_stop
async def cleanup(*args, **kwargs):
    await httpClient.aclose()

    raw_producer.flush() if raw_producer is not None else None
    state_update_producer.flush() if state_update_producer is not None else None

    pulsar_client.close()

    await token_channel.unsubscribe()


@app.post('/room/<room:str>')  # register room
async def room_post(request: Request, room: str):
    prefix = 'http://pulsar:8080/admin/v2/persistent/public/default'
    resp = await httpClient.put(f'{prefix}/{room}')
    if resp.status_code not in {204, 409}:
        return text(f'create danmaku topic error: {resp.status_code}', status=resp.status_code)

    resp = await httpClient.put(f'{prefix}/user_{room}')
    if resp.status_code not in {204, 409}:
        return text(f'create user topic error: {resp.status_code}', status=resp.status_code)

    resp = await httpClient.post(f'{prefix}/{room}/permissions/display_{room}', json=['consume'])
    if resp.status_code != 204:
        return text(text=f'grant permission error: {resp.status_code}', status=resp.status_code)

    resp = await httpClient.post(f'{prefix}/user_{room}/permissions/display_{room}', json=['consume'])
    if resp.status_code != 204:
        return text(text=f'grant permission error: {resp.status_code}', status=resp.status_code)

    token = jwt.encode({'sub': f'display_{room}'}, private_key, algorithm='RS256', headers={'typ': None})
    return text(token)


@app.put('/token/<room:str>')  # replace wechat access token
async def token_put(request: Request, room: str):
    binary: bytes = request.body
    await redis.publish('access_token', f'{room}:{binary.decode()}')
    return text('success')


@app.put('/setting/<room:str>')  # replace room setting
async def setting_put(request: Request, room: str):
    state_binary: bytes = request.body
    get_state_update_producer().send_async(
        content=json.dumps([room, state_binary.decode()]).encode(),
        callback=lambda *_: None
    )
    return text('success')


@app.post('/port/<room:str>')  # wechat send danmaku
async def port_post(request: Request, room: str):
    root = ElementTree.fromstring(request.body)
    data: Mapping[str, str] = {el.tag: el.text for el in root}
    message_type = data.get('MsgType', '')
    if message_type == 'event':
        # TODO:
        return

    content = data.get('Content', '')
    from_user = data.get('FromUserName', '')
    sender = 'user@wechat:' + from_user  # add user@wechat: prefix; client should strip this before getting the avatar
    developer_account = data.get('ToUserName', '')

    if message_type != 'text' or content == '【收到不支持的消息类型，暂无法显示】':
        reply_message = os.getenv('WECHAT_DANMAKU_REPLY_FAIL', '暂不支持这种消息哦')
    else:
        get_raw_producer().send_async(
            content=json.dumps(
                dict(
                    content=content,
                    sender=sender,
                    room=room,
                ),
                ensure_ascii=False
            ).encode(),
            callback=lambda *_: None
        )
        reply_message = os.getenv('WECHAT_DANMAKU_REPLY_SUCCESS', '收到你的消息啦，之后会推送上墙~')

    response_xml = (f'''
<xml>
    <ToUserName><![CDATA[{from_user}]]></ToUserName>
    <FromUserName><![CDATA[{developer_account}]]></FromUserName>
    <CreateTime>{int(time())}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{reply_message}]]></Content>
</xml>
    ''')
    return text(response_xml, content_type='text/xml')

wechat_token_length = int(os.getenv('WECHAT_TOKEN_LEN', '12'))
wechat_token_salt = os.getenv('WECHAT_TOKEN_SALT').encode()


def readable_sha256(binary: bytes, readable_char_table=bytes.maketrans(b'l1I0O+/=', b'LLLooXYZ')) -> str:
    return b2a_base64(sha256(binary).digest(), newline=False).translate(readable_char_table).decode()


@app.get('/port/<room:str>')  # wechat access
async def port_get(request: Request, room: str):
    token = readable_sha256(room.encode() + wechat_token_salt)[:wechat_token_length]
    query = request.get_args()
    timestamp = query.get('timestamp', '')
    nonce = query.get('nonce', '')
    signature = query.get('signature', '')

    tmpArr = [token, timestamp, nonce]
    tmpArr.sort()
    if sha1(''.join(tmpArr).encode('utf-8')).hexdigest() == signature:
        echostr = query.get('echostr', '')
        return text(echostr)

    return text('Wrong signature!', status=403)


app.run(host='0.0.0.0', port=8000, workers=2)
