import asyncio
from hashlib import sha1, sha256
from binascii import b2a_base64
import json
from xml.etree import ElementTree
from time import time
import os

from typing import Any, Callable, Mapping, MutableMapping, MutableSet, Optional, Sequence, Union

from cryptography.hazmat.primitives import serialization
import jwt

import aioredis
from aioredis.client import PubSub
from httpx import AsyncClient
from sanic import Sanic, Request, text
import pulsar

with open('/private_key/private.key', 'rb') as f:
    private_key = serialization.load_der_private_key(f.read(), None)
# jwt's key can be cryptography key object or str(PEM/SSH or HMAC secret)
super_user_token = jwt.encode({'sub': 'super-user'}, private_key, algorithm='RS256', headers={'typ': None})

http_client = AsyncClient(headers={'Authorization': f'Bearer {super_user_token}'})
pulsar_client = pulsar.Client('pulsar://pulsar:6650', pulsar.AuthenticationToken(super_user_token))
raw_producer: Optional[pulsar.Producer] = None
state_update_producer: Optional[pulsar.Producer] = None
user_producers: MutableMapping[str, pulsar.Producer] = {}

redis: aioredis.Redis = aioredis.from_url('redis://redis:6379/0', encoding="utf-8", decode_responses=True)
token_channel = redis.pubsub()
token_cache: MutableMapping[str, str] = {}
user_channel = redis.pubsub()
user_cache: MutableMapping[str, MutableSet] = {}
room_exist_channel = redis.pubsub()
room_exist_cache: MutableSet[str] = set()
room_enable_channel = redis.pubsub()
room_enable_cache: MutableSet[str] = set()

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
            block_if_queue_full=True,
            batching_enabled=True,
            batching_max_publish_delay_ms=100
        )
    return user_producers[room]


def sync_worker(pubsub: PubSub, channel: str, func: Callable[[str, str], None]):
    async def wrapper():
        await pubsub.subscribe(channel)
        while pubsub.subscribed:
            message = pubsub.handle_message(await pubsub.parse_response(block=True), ignore_subscribe_messages=True)
            if message is None:
                continue
            data: str = message['data']
            func(*data.split(':'))
    
    app.add_task(wrapper())


@app.before_server_start
async def setup(*args, **kwargs):
    def sync_token_cache(key: str, value: str):
        token_cache[key] = value
    sync_worker(token_channel, 'access_token', sync_token_cache)

    # TODO: read from pulsar to recover data
    def sync_user_cache(key: str, value: str):
        if key not in user_cache:
            user_cache[key] = set()
        user_cache[key].add(value)
    sync_worker(user_channel, 'room_user', sync_user_cache)

    def sync_set_cache(set_cache: MutableSet):
        def sync(key: str, value: str):
            if value == '0':
                return set_cache.remove(key)
            if value == '1':
                return set_cache.add(key)
        return sync
    sync_worker(room_exist_channel, 'room_exist', sync_set_cache(room_exist_cache))
    sync_worker(room_enable_channel, 'room_enable', sync_set_cache(room_enable_cache))


@app.after_server_stop
async def cleanup(*args, **kwargs):
    await http_client.aclose()

    raw_producer.flush() if raw_producer is not None else None
    state_update_producer.flush() if state_update_producer is not None else None

    pulsar_client.close()

    await room_enable_channel.unsubscribe()
    await room_exist_channel.unsubscribe()
    await user_channel.unsubscribe()
    await token_channel.unsubscribe()


@app.post('/room/<room:str>')  # register room
async def room_post(request: Request, room: str):
    prefix = 'http://pulsar:8080/admin/v2/persistent/public/default'
    resp = await http_client.put(f'{prefix}/{room}')
    if resp.status_code not in {204, 409}:
        return text(f'create danmaku topic error: {resp.status_code}', status=resp.status_code)

    resp = await http_client.put(f'{prefix}/user_{room}')
    if resp.status_code not in {204, 409}:
        return text(f'create user topic error: {resp.status_code}', status=resp.status_code)

    resp = await http_client.post(f'{prefix}/{room}/permissions/display_{room}', json=['consume'])
    if resp.status_code != 204:
        return text(text=f'grant permission error: {resp.status_code}', status=resp.status_code)

    resp = await http_client.post(f'{prefix}/user_{room}/permissions/display_{room}', json=['consume'])
    if resp.status_code != 204:
        return text(text=f'grant permission error: {resp.status_code}', status=resp.status_code)

    await redis.publish('room_exist', f'{room}:1')

    token = jwt.encode({'sub': f'display_{room}'}, private_key, algorithm='RS256', headers={'typ': None})
    return text(token)


@app.post('/feed/<room:str>')  # fetch and push user info
async def feed_post(request: Request, room: str):
    if room not in room_exist_cache:
        return text('room not found', status=404)
    if room not in token_cache:
        return text('room access token not found', status=403)

    token = token_cache[room]
    resp = await http_client.get(
        'https://api.weixin.qq.com/cgi-bin/user/get',
        params={'access_token': token}
    )
    # TODO: > 10000 user, nextopenid
    if resp.status_code != 200:
        return text('Error fetch from wechat', status=500)
    resp_obj: Mapping[str, Any] = resp.json()
    if 'errcode' in resp_obj:
        return text('Error fetch from wechat', status=500)
    users: Sequence[str] = resp_obj['data']['openid']

    producer = get_user_producer(room)
    async def feed():
        batch_size = 100
        for i in range(0, len(users), batch_size):
            def batchget():
                return http_client.post(
                    'https://api.weixin.qq.com/cgi-bin/user/info/batchget',
                    json={'user_list':[{'openid': openid} for openid in users[i:i + batch_size]]},
                    params={'access_token': token}
                )
            resp = await batchget()
            while not resp.is_success:
                await asyncio.sleep(2.0)
                resp = await batchget()
            resp_obj: Mapping[str, Any] = resp.json()
            if 'errorcode' in resp_obj:
                break # TODO: error handling
            user_info_list: Sequence[Mapping[str, Union[str, Any]]] = resp_obj['user_info_list']
            data_list = [
                dict(
                    id='user@wechat:' + user_info['openid'],
                    nickname=user_info['nickname'],
                    headimgurl=user_info['headimgurl']
                ) for user_info in user_info_list if user_info['subscribe']
            ]
            for data in data_list:
                producer.send_async(
                    b'\x00\x00\x02',
                    callback=lambda *_: None,
                    properties=data
                )
    app.add_task(feed())
    return text('success')


@app.put('/token/<room:str>')  # replace wechat access token
async def token_put(request: Request, room: str):
    binary: bytes = request.body
    await redis.publish('access_token', f'{room}:{binary.decode()}')
    return text('success')


@app.put('/setting/<room:str>')  # replace room setting
async def setting_put(request: Request, room: str):
    if room not in room_exist_cache:
        return text('room not found', status=404)

    state: MutableMapping = json.loads(request.body)
    enable = int(state['danmaku_enabled'])
    await redis.publish('room_enable', f'{room}:{enable}')
    del state['danmaku_enabled']
    get_state_update_producer().send_async(
        content=json.dumps([room, json.dumps(state)]).encode(),
        callback=lambda *_: None
    )
    return text('success')


room_not_found = '房间不存在'
room_disable = '房间未开启弹幕'
not_support = os.getenv('WECHAT_DANMAKU_REPLY_FAIL', '暂不支持这种消息哦')
success = os.getenv('WECHAT_DANMAKU_REPLY_SUCCESS', '收到你的消息啦，之后会推送上墙~')


@app.post('/port/<room:str>')  # wechat send danmaku
async def port_post(request: Request, room: str):
    data: Mapping[str, str] = {el.tag: el.text for el in ElementTree.fromstring(request.body)}
    from_user = data.get('FromUserName', '')
    developer_account = data.get('ToUserName', '')

    def reply_xml(reply_message: str):
        return text(f'''
            <xml>
                <ToUserName><![CDATA[{from_user}]]></ToUserName>
                <FromUserName><![CDATA[{developer_account}]]></FromUserName>
                <CreateTime>{int(time())}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{reply_message}]]></Content>
            </xml>''',
                    content_type='text/xml'
                    )

    if room not in room_exist_cache:
        return reply_xml(room_not_found)
    if room not in room_enable_cache:
        return reply_xml(room_disable)

    message_type = data.get('MsgType', '')
    if message_type not in {'text', 'event'}:
        return reply_xml(not_support)

    if message_type == 'event':
        # TODO
        event = data.get('Event', '')
        return text('success')

    content = data.get('Content', '')
    if content == '【收到不支持的消息类型，暂无法显示】':
        return reply_xml(not_support)

    sender = 'user@wechat:' + from_user  # add user@wechat: prefix; client should strip this before getting the avatar
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
    return reply_xml(success)


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
