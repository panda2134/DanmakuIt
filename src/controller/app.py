import json
from hashlib import sha1, sha256
from binascii import b2a_base64
from xml.etree import ElementTree
import os

from typing import Mapping, Optional, Union

from cryptography.hazmat.primitives import serialization
import jwt

from httpx import AsyncClient
from sanic import Sanic, Request, text, json as objectNotation
import pulsar

with open('/private_key/private.key', 'rb') as f:
    private_key = serialization.load_der_private_key(f.read(), None)
# jwt's key can be cryptography key object or str(PEM/SSH or HMAC secret)
super_user_token = jwt.encode({'sub': 'super-user'}, private_key, algorithm='RS256', headers={'typ': None})
super_user_headers = {'Authorization': f'Bearer {super_user_token}'}
 
httpClient = AsyncClient()
pulsar_client = pulsar.Client('pulsar://pulsar:6650', pulsar.AuthenticationToken(super_user_token))
raw_producer: Optional[pulsar.Producer] = None
state_update_producer: Optional[pulsar.Producer] = None

app = Sanic('Controller')


@app.after_server_stop
async def cleanup(*args, **kwargs):
    await httpClient.aclose()

    raw_producer.flush() if raw_producer is not None else None
    state_update_producer.flush() if state_update_producer is not None else None

    pulsar_client.close()


@app.post('/room/<room:str>')  # creat room
async def room_post(request: Request, room: str):
    resp = await httpClient.put(f'http://pulsar:8080/admin/v2/persistent/public/default/{room}', headers=super_user_headers)
    if resp.status_code not in {204, 409}:
        return text(f'create topic error: {resp.status_code}', status=resp.status_code)
    resp = await httpClient.post(f'http://pulsar:8080/admin/v2/persistent/public/default/{room}/permissions/display_{room}',
                                 json=['consume'],
                                 headers=super_user_headers)
    if resp.status_code != 204:
        return text(text=f'grant permission error: {resp.status_code}', status=resp.status_code)
    token = jwt.encode({'sub': f'display_{room}'}, private_key, algorithm='RS256', headers={'typ': None})
    return text(token)


@app.post('/port/<room:str>')  # wechat send danmaku
async def port_post(request: Request, room: str):
    root = ElementTree.fromstring(request.body)
    data: Mapping[str, str] = {el.tag: el.text for el in root}
    content = data.get('Content', '')
    message_type = data.get('MsgType', 'text')
    sender = 'user_' + data.get('FromUserName', '')
    developer_account = data.get('ToUserName', '')
    create_time = data.get('CreateTime', 0)

    if message_type == 'text' and content != '【收到不支持的消息类型，暂无法显示】':
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
        reply_message = os.getenv('WECHAT_DANMAKU_REPLY_SUCCESS', '收到你的消息啦，之后会推送上墙~')
    else:
        reply_message = os.getenv('WECHAT_DANMAKU_REPLY_FAIL', '暂不支持这种消息哦')
    
    return text(f'''<xml>
                <ToUserName><![CDATA[{sender}]]></ToUserName>
                <FromUserName><![CDATA[{developer_account}]]></FromUserName>
                <CreateTime>{create_time}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{reply_message}]]></Content>
                </xml>
                ''',
            content_type='text/xml')

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


@app.post('/setting/<room:str>')  # replace room setting
async def setting_post(request: Request, room: str):
    state_binary: bytes = request.body
    global state_update_producer
    if state_update_producer is None:
        state_update_producer = pulsar_client.create_producer(
            'persistent://public/default/state',
            block_if_queue_full=True
        )

    def callback(res, msg_id): pass

    state_update_producer.send_async(
        content=json.dumps([room, state_binary.decode()]).encode(),
        callback=callback
    )
    return text('success')


@app.get('/setting/<room:str>')  # get room setting
async def setting_get(request: Request, room: str):
    resp = await httpClient.get(f'http://pulsar:8080/admin/v3/functions/public/default/tagger/state/{room}', headers=super_user_headers)
    obj: Mapping[str, Union[str, int]] = resp.json()
    print('Settings:', obj) # TODO: Remove debug log
    if 'stringValue' not in obj:
        return text('setting is not initialized', status=404)
    return text(obj['stringValue'])


@app.get('/debug/<room:str>')
async def debug_room(request: Request, room: str):
    reader = pulsar_client.create_reader(f'persistent://public/default/{room}', start_message_id=pulsar.MessageId.earliest)
    msgs = []
    while reader.has_message_available():
        # receive/read_next will block whole server if there is no message available
        msg = reader.read_next().properties()
        msgs.append(msg)

    return objectNotation(msgs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=2)
