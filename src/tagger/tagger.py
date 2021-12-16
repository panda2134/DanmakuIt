import asyncio
import threading
import time
import os
import random
import binascii
import json
import re

from typing import Any, Mapping, MutableMapping, Optional, Sequence

from httpx import AsyncClient
from pulsar import Function, Context, SerDe, Message
import pulsar


class BytesIdentity(SerDe):  # Real Identity, not str()
    @staticmethod
    def serialize(x: bytes):
        return x

    @staticmethod
    def deserialize(x: bytes):
        return x

class TaggingContext(object):
    def __init__(self):
        super().__init__()
        self.loop: asyncio.AbstractEventLoop = None
        with open('/token/super_user') as f: # TODO: fetch from controller
            super_user_token = f.read()
        self.client = pulsar.Client('pulsar://pulsar:6650', pulsar.AuthenticationToken(super_user_token))
        self.state_reader: Optional[pulsar.Reader] = None
        self.publish_producers: MutableMapping[str, pulsar.Producer] = {}

        self.state: Mapping[str, dict] = {}
        self.state_re: Mapping[str, Sequence[re.Pattern]] = {}
    
    async def setup(self):
        self.loop = asyncio.get_event_loop()
        self.state_reader = await self.get_state_reader()

    async def get_state_reader(self):
        while True:
            try:
                return self.client.create_reader(
                    f'persistent://public/default/state',
                    start_message_id=pulsar.MessageId.earliest,
                    reader_listener=self.state_listener
                )
            except:
                await asyncio.sleep(10.0)
    
    def state_listener(self, _, message: Message):
        room, state_str = json.loads(message.data())
        room_state: Mapping[str, Any] = json.loads(state_str)
        print('get state', room, room_state)
        asyncio.run_coroutine_threadsafe(self.update_state(room, room_state), self.loop) # avoid concurrent, run in same event loop

    async def update_state(self, room: str, room_state: Mapping[str, Any]):
        self.state[room] = {key: room_state[key] for key in ('remote_censor', 'user_danmaku_colors')}
        self.state_re[room] = [re.compile('.*?'.join(list(keyword))) for keyword in room_state['keyword_blacklist']]

    async def publish(self, room, properties: Mapping[str, str]):
        if room not in self.publish_producers:
            self.publish_producers[room] = self.client.create_producer(
                f'persistent://public/default/{room}',
                block_if_queue_full=True,
                batching_enabled=True,
                batching_max_publish_delay_ms=10,
            )

        self.publish_producers[room].send_async(
            content=b'\x00\x00\x00',
            callback=lambda *_: None,
            properties=properties
        )


class TaggingFunction(Function):
    def __init__(self):
        super().__init__()
        self.access_token = ''
        self.access_token_expiration = 0.0
        self.access_token_refetch_margin = 2e5  # sec
        self.remote_censor_max_retry_times = 10

        self.loop = loop = asyncio.new_event_loop()

        def run_background_event_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()
        threading.Thread(target=run_background_event_loop, daemon=True).start()

        self.http_client = AsyncClient()

        asyncio.run_coroutine_threadsafe(self.fetch_access_token(), loop)  # infinite loop fetch access token
        
        self.context = TaggingContext()
        asyncio.run_coroutine_threadsafe(self.context.setup(), loop)

    def __del__(self):
        asyncio.run_coroutine_threadsafe(self.http_client.aclose(), self.loop).result()  # blocking

    async def fetch_access_token(self):
        params = dict(
            grant_type='client_credentials',
            client_id=os.getenv('BAIDU_CLIENT_ID'),
            client_secret=os.getenv('BAIDU_CLIENT_SECRET')
        )
        while True:
            resp = await self.http_client.post('https://aip.baidubce.com/oauth/2.0/token', params=params)
            resp_obj: Mapping = resp.json()
            if 'error' not in resp_obj:
                self.access_token = resp_obj['access_token']
                delta_time = float(resp_obj['expires_in'])
                self.access_token_expiration = time.time() + delta_time
                await asyncio.sleep(max(5.0, delta_time - self.access_token_refetch_margin))
            else:
                print('fetch access token fail')
                await asyncio.sleep(5.0)  # retry 5s

    async def remote_censor(self, text: str, retry_times: int = 0) -> bool:
        while self.access_token_expiration < time.time():
            await asyncio.sleep(1.0)  # blocking until new access token has been fetched

        resp = await self.http_client.post('https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined',
                                          params=dict(access_token=self.access_token),
                                          data=f'text={text}',
                                          headers={'content-type': 'application/x-www-form-urlencoded'})
        resp_obj: Mapping = resp.json()
        result: Optional[int] = resp_obj.get('conclusionType')
        if result is not None:
            return (result == 1)

        if resp_obj.get('error_code') != 18 or retry_times >= self.remote_censor_max_retry_times:
            return False

        # qps limit, retry after [1.0, 4.0) sec
        await asyncio.sleep(1.0 + random.random() * 3.0)
        return await self.remote_censor(text, retry_times + 1)

    async def tag(self, input: bytes):
        obj: Mapping[str, str] = json.loads(input)

        content = obj['content']
        room = obj['room']

        room_state = self.context.state.get(room, {})
        patterns = self.context.state_re.get(room, [])
        permission = False  # when remote censor is off, every danmaku shall be checked manually
        if room_state.get('remote_censor'):
            permission = all(p.search(content) is None for p in patterns)
            if permission:
                permission = await self.remote_censor(content)
        
        colors = room_state.get('user_danmaku_colors') or ['undefined']

        await self.context.publish(
            room=room,
            properties=dict(
                content=content,
                id=binascii.b2a_base64(os.urandom(24), newline=False).decode(),
                sender=obj['sender'],
                permission='1' if permission else '0',  # properties must be string
                color=random.choice(colors),
                size=room_state.get('size', '16pt'),
                pos=room_state.get('pos', 'rightleft')
            )
        )

    def process(self, input: bytes, _: Context):
        # WARNING: "current message" of context will be updated by main thread
        # should not get message info from context object in async functions
        asyncio.run_coroutine_threadsafe(self.tag(input), self.loop)
