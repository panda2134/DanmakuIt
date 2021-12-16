import asyncio
from hashlib import sha1, sha256
from binascii import b2a_base64
import json as jsonlib
from xml.etree import ElementTree
from time import time
import os
from collections import defaultdict

from typing import Any, Callable, Mapping, MutableMapping, MutableSet, Optional, Sequence, Union

from cryptography.hazmat.primitives import serialization
import jwt

import aioredis
from aioredis.client import PubSub
from httpx import AsyncClient
from sanic import Sanic, Request, text, json
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
danmaku_producers: MutableMapping[str, pulsar.Producer] = {}

redis: aioredis.Redis = aioredis.from_url('redis://redis:6379/0', encoding="utf-8", decode_responses=True)
token_channel = redis.pubsub()
token_cache: MutableMapping[str, str] = {}
user_channel = redis.pubsub()
user_cache: MutableMapping[str, MutableSet[str]] = defaultdict(set)
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

def get_danmaku_producer(room: str) -> pulsar.Producer:
    if room not in danmaku_producers:
        danmaku_producers[room] = pulsar_client.create_producer(
            f'persistent://public/default/{room}',
            block_if_queue_full=True,
            batching_enabled=True,
            batching_max_publish_delay_ms=10
        )
    return danmaku_producers[room]


def get_user_producer(room: str):
    if room not in user_producers:
        user_producers[room] = pulsar_client.create_producer(
            f'persistent://public/default/user_{room}',
            block_if_queue_full=True,
            batching_enabled=True,
            batching_max_publish_delay_ms=100
        )
    return user_producers[room]

async def succeed_subscription(pubsub: PubSub, channel: str):
    while True:
        try:
            return await pubsub.subscribe(channel)
        except aioredis.ConnectionError:
            await asyncio.sleep(1.0)

async def get_message(pubsub: PubSub):
    while True:
        try:
            await pubsub.connection.connect() # try reconnect, immediate return when connected
            response = await pubsub.parse_response(block=True)
            message = pubsub.handle_message(response, ignore_subscribe_messages=True)
            if message is not None:
                return message
        except aioredis.ConnectionError:
            await asyncio.sleep(1.0) # TODO: may lose cache consistency during reconnection

async def start_sync_worker(pubsub: PubSub, channel: str, func: Callable[[str, str], None]):
    await succeed_subscription(pubsub, channel) # block until successfully subscribe
    async def wrapper():
        while True:
            message = await get_message(pubsub)
            data: str = message['data']
            func(*data.split(':', maxsplit=1))
    app.add_task(wrapper())

def remove_key(mapping: MutableMapping[Any, Any], key: Any):
    mapping.pop(key, None)

@app.before_server_start
async def setup(*args, **kwargs):
    def sync_token_cache(key: str, value: str):
        token_cache[key] = value

    await start_sync_worker(token_channel, 'access_token', sync_token_cache) # block until setup succeed

    def sync_user_cache(key: str, value: str):
        if key == 'remove':
            return remove_key(user_cache, value)
        user_cache[key].add(value)

    await start_sync_worker(user_channel, 'room_user', sync_user_cache)

    def sync_set_cache(set_cache: MutableSet):
        def sync(key: str, value: str):
            if value == '0':
                return set_cache.discard(key)
            if value == '1':
                return set_cache.add(key)

        return sync

    await start_sync_worker(room_exist_channel, 'room_exist', sync_set_cache(room_exist_cache))
    await start_sync_worker(room_enable_channel, 'room_enable', sync_set_cache(room_enable_cache))


@app.after_server_stop
async def cleanup(*args, **kwargs):
    await http_client.aclose()

    raw_producer.flush() if raw_producer is not None else None
    state_update_producer.flush() if state_update_producer is not None else None
    for v in user_producers.values():
        v.flush()
    for v in danmaku_producers.values():
        v.flush()

    pulsar_client.close()

    await room_enable_channel.unsubscribe()
    await room_exist_channel.unsubscribe()
    await user_channel.unsubscribe()
    await token_channel.unsubscribe()


@app.get('/room/<room:str>/consumers')  # get online consumers
async def get_consumers(request: Request, room: str):
    if room not in room_enable_cache:
        return json({
            'code': 404,
            'message': 'room not enabled'
        }, status=404)
    prefix = 'http://pulsar:8080/admin/v2/persistent/public/default'
    res = await http_client.get(prefix + f'/{room}/stats')
    if res.status_code != 200:
        return text(f'cannot get consumers of room {room}', status=500)
    subscriptions = res.json()['subscriptions']
    return json({k: v['consumers'] for (k, v) in subscriptions.items() if len(v['consumers'])})


@app.post('/room/<room:str>')  # register room
async def room_post(request: Request, room: str):
    prefix = 'http://pulsar:8080/admin/v2/persistent/public/default'
    resp = await http_client.put(f'{prefix}/{room}')
    if not resp.is_success: # 409 when topic duplicate: reject reuse room
        return text(f'create danmaku topic error: {resp.status_code}', status=500)

    resp = await http_client.put(f'{prefix}/user_{room}')
    if not resp.is_success:
        # It is impossible to do atomic transaction through stateless RESTful API
        return text(f'create user topic error: {resp.status_code}', status=500)

    infinite_retention = dict(retentionTimeInMinutes=-1, retentionSizeInMB=-1)

    resp = await http_client.post(f'{prefix}/{room}/retention', json=infinite_retention)
    if not resp.is_success:
        return text(f'danmaku topic set retention error: {resp.status_code}', status=500)

    resp = await http_client.post(f'{prefix}/user_{room}/retention', json=infinite_retention)
    if not resp.is_success:
        return text(f'user topic set retention error: {resp.status_code}', status=500)

    resp = await http_client.post(f'{prefix}/{room}/permissions/display_{room}', json=['consume'])
    if not resp.is_success:
        return text(f'danmaku topic grant permission error: {resp.status_code}', status=500)

    resp = await http_client.post(f'{prefix}/user_{room}/permissions/display_{room}', json=['consume'])
    if not resp.is_success:
        return text(f'user topic grant permission error: {resp.status_code}', status=500)

    room_exist_cache.add(room)
    await redis.publish('room_exist', f'{room}:1')

    token = jwt.encode({'sub': f'display_{room}'}, private_key, algorithm='RS256', headers={'typ': None})
    return text(token)


@app.delete('/room/<room:str>')
async def room_delete(request: Request, room: str):
    prefix = 'http://pulsar:8080/admin/v2/persistent/public/default'
    resp = await http_client.delete(f'{prefix}/{room}/permissions/display_{room}')
    if not resp.is_success:
        return text(f'danmaku topic revoke permission error: {resp.status_code}', status=500)

    resp = await http_client.delete(f'{prefix}/user_{room}/permissions/display_{room}')
    if not resp.is_success:
        return text(f'user topic revoke permission error: {resp.status_code}', status=500)

    no_retention = dict(retentionTimeInMinutes=0, retentionSizeInMB=0)

    resp = await http_client.post(f'{prefix}/{room}/retention', json=no_retention)
    if not resp.is_success:
        return text(f'danmaku topic set retention error: {resp.status_code}', status=500)

    resp = await http_client.post(f'{prefix}/user_{room}/retention', json=no_retention)
    if not resp.is_success:
        return text(f'user topic set retention error: {resp.status_code}', status=500)
    
    room_exist_cache.discard(room)
    room_enable_cache.discard(room)
    remove_key(user_cache, room)
    await redis.publish('user_cache', f'remove:{room}')
    await redis.publish('room_enable', f'{room}:0')
    await redis.publish('room_exist', f'{room}:0')
    return text('success')

async def fetch_users(room: str, users: Sequence[str]):
    token = token_cache[room]
    producer = get_user_producer(room)

    def batch_get_user_info():
        return http_client.post(
            'https://api.weixin.qq.com/cgi-bin/user/info/batchget',
            json={'user_list': [{'openid': openid} for openid in users]},
            params={'access_token': token}
        )

    retry = 0
    while not (resp := await batch_get_user_info()).is_success:
        if (retry := retry + 1) > 5:
            return False
        await asyncio.sleep(2.0)

    resp_obj: Mapping[str, Any] = resp.json()
    if 'errcode' in resp_obj:
        print('Error retrieving user info list')
        return False
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
        user_cache[room].add(data['id'])
        await redis.publish('room_user', f'{room}:{data["id"]}')
    return True


@app.post('/feed/<room:str>')  # fetch and push user info
async def feed_post(request: Request, room: str):
    if room not in room_exist_cache:
        return text('room not found', status=404)
    if room not in token_cache:
        return text('room access token not found', status=403)

    token = token_cache[room]
    users = []
    next_openid: Optional[str] = None
    while True:
        next_openid_query = f'&next_openid={next_openid}' if next_openid is not None else ''
        resp = await http_client.get(f'https://api.weixin.qq.com/cgi-bin/user/get?access_token={token}{next_openid_query}')
        if resp.status_code != 200:
            return text('Error fetch from wechat', status=500)
        resp_obj: Mapping[str, Any] = resp.json()
        if 'errcode' in resp_obj:
            return text('Error fetch from wechat', status=500)
        users.extend(resp_obj['data']['openid'])
        if len(users) >= resp_obj['total']:
            break
        next_openid = resp_obj['next_openid']
        if type(next_openid) is not str or len(next_openid) == 0:
            return text('Error fetch from wechat', status=500)

    async def feed():
        batch_size = 100
        for i in range(0, len(users), batch_size):
            if not await fetch_users(room, users[i:i + batch_size]):
                break # TODO: error handling

    app.add_task(feed())
    return text('success')


@app.put('/token/<room:str>')  # replace wechat access token
async def token_put(request: Request, room: str):
    token = str(request.body, 'utf-8')
    token_cache[room] = token
    await redis.publish('access_token', f'{room}:{token}')
    return text('success')

async def resume_user_cache(room: str):
    while True:
        try:
            reader = pulsar_client.create_reader(
                f'persistent://public/default/user_{room}',
                start_message_id=pulsar.MessageId.earliest
            )
            break
        except:
            await asyncio.sleep(30.0)
    while True:
        try:
            message = reader.read_next(timeout_millis=3)
            data: Mapping[str, str] = message.properties()
            user_cache[room].add(data['id'])
            await redis.publish('room_user', f'{room}:{data["id"]}')
        except:
            break
    reader.close()

@app.put('/setting/<room:str>')  # replace room setting
async def setting_put(request: Request, room: str):
    mode: Optional[str] = request.get_args().get('mode')
    if room not in room_exist_cache:
        if mode is None:
            return text('room not found', status=404)
        if mode == 'resume':
            room_exist_cache.add(room)
            await redis.publish('room_exist', f'{room}:1')
            await resume_user_cache(room) # can take long time

    state: MutableMapping = jsonlib.loads(request.body)
    enable = int(state['danmaku_enabled'])
    (room_enable_cache.add if enable else room_enable_cache.discard)(room)
    await redis.publish('room_enable', f'{room}:{enable}')
    del state['danmaku_enabled']
    # we don't know whether pulsar client is thread safe
    # cannot use to_thread(py3.9) or run_in_executor to simplify logic
    # just poll ack
    ack_reader = pulsar_client.create_reader(
        f'persistent://public/default/ack_{room}',
        start_message_id=pulsar.MessageId.latest
    )
    get_state_update_producer().send_async(
        content=jsonlib.dumps([room, jsonlib.dumps(state)]).encode(),
        callback=lambda *_: None
    )
    while not ack_reader.has_message_available(): # what about concurrent state update's ack?
        await asyncio.sleep(0.3) # do we need timeout?
    ack_reader.close()
    return text('success')


@app.post('/danmaku-alter/<room:str>')  # post danmaku
async def danmaku_alter_post(request: Request, room: str):
    danmaku: Mapping[str, str] = request.json
    req_type = request.get_args().get('type', 'update')
    if req_type != 'update' and req_type != 'send':
        return text('bad request', status=400)
    content = b'\x00\x00\x00' if req_type == 'send' else b'\x00\x00\x01'
    get_danmaku_producer(room).send_async(
        content=content,
        properties=danmaku,
        callback=lambda *_: None
    )
    return text('success')


room_not_found = '房间不存在'
room_disable = '房间未开启弹幕'
not_support = os.getenv('WECHAT_DANMAKU_REPLY_NOT_SUPPORT', '暂不支持这种消息哦~')
danmaku_maxlen = int(os.getenv('WECHAT_DANMAKU_MAXLEN', '50'))
exceed_maxlen = os.getenv('WECHAT_DANMAKU_REPLY_EXCEED_MAXLEN', '暂时没法处理这么长的消息哦~')
success = os.getenv('WECHAT_DANMAKU_REPLY_SUCCESS', '收到你的消息啦，之后会推送上墙~')


wechat_token_length = int(os.getenv('WECHAT_TOKEN_LEN', '12'))
wechat_token_salt = os.getenv('WECHAT_TOKEN_SALT').encode()


def readable_sha256(binary: bytes, readable_char_table=bytes.maketrans(b'l1I0O+/=', b'LLLooXYZ')) -> str:
    return b2a_base64(sha256(binary).digest(), newline=False).translate(readable_char_table).decode()


def get_token(room: str):
    return readable_sha256(room.encode() + wechat_token_salt)[:wechat_token_length]


@app.post('/port/<room:str>')  # wechat send danmaku
async def port_post(request: Request, room: str):
    token: Optional[str] = request.get_args().get('token')
    if token != get_token(room):
        return text('token error', status=401)

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
                    content_type='text/xml')

    if room not in room_exist_cache:
        return reply_xml(room_not_found)
    if room not in room_enable_cache:
        return reply_xml(room_disable)

    message_type = data.get('MsgType', '')
    if message_type not in {'text', 'event'}:
        return reply_xml(not_support)

    if message_type == 'event':
        event = data.get('Event', '')
        if event == 'subscribe':
            app.add_task(fetch_users(room, [from_user]))
        return text('success')

    content = data.get('Content', '')
    if content == '【收到不支持的消息类型，暂无法显示】':
        return reply_xml(not_support)
    
    if len(content) > danmaku_maxlen:
        return reply_xml(exceed_maxlen)

    sender = 'user@wechat:' + from_user
    if room not in user_cache or sender not in user_cache[room]:
        app.add_task(fetch_users(room, [from_user]))
    get_raw_producer().send_async(
        content=jsonlib.dumps(
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
