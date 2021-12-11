import asyncio
import threading
import time
import os
import random
import binascii
import json
import re

from typing import Any, Mapping, Optional, Sequence

from httpx import AsyncClient
from pulsar import Function, Context, SerDe


class BytesIdentity(SerDe):  # Real Identity, not str()
    @staticmethod
    def serialize(x: bytes):
        return x

    @staticmethod
    def deserialize(x: bytes):
        return x


class TaggingFunction(Function):
    def __init__(self):
        self.access_token = ''
        self.access_token_expiration = 0.0
        self.access_token_refetch_margin = 2e5  # sec
        self.remote_censor_max_retry_times = 10

        self.loop = loop = asyncio.new_event_loop()

        def run_background_event_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()
        threading.Thread(target=run_background_event_loop, daemon=True).start()

        self.httpClient = AsyncClient()

        asyncio.run_coroutine_threadsafe(self.fetch_access_token(), loop)  # infinite loop fetch access token

        self.state_cache: Mapping[str, dict] = {}
        self.re_cache: Mapping[str, Sequence[re.Pattern]] = {}

    def __del__(self):
        asyncio.run_coroutine_threadsafe(self.httpClient.aclose(), self.loop).result()  # blocking

    async def fetch_access_token(self):
        params = dict(
            grant_type='client_credentials',
            client_id='s7tl79bgMTtcuHkHZQ0WZp79',
            client_secret='D01hLswaLGzGOnPI6cCB8I0HCX9ljEGH'
        )
        while True:
            resp = await self.httpClient.post('https://aip.baidubce.com/oauth/2.0/token', params=params)
            resp_obj: Mapping = resp.json()
            if 'error' not in resp_obj:
                self.access_token = resp_obj['access_token']
                delta_time = float(resp_obj['expires_in'])
                self.access_token_expiration = time.time() + delta_time
                await asyncio.sleep(max(5.0, delta_time - self.access_token_refetch_margin))
            else:
                print('fetch access token fail')
                await asyncio.sleep(5.0)  # retry 5s

    async def remote_censor(self, text: str, retry_times: int = 0):
        while self.access_token_expiration < time.time():
            await asyncio.sleep(1.0)  # blocking until new access token has been fetched

        resp = await self.httpClient.post('https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined',
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

    async def tag(self, input: bytes, context: Context):
        obj: Mapping[str, str] = json.loads(input.decode())

        content = obj['content']
        room = obj['room']

        room_state = self.state_cache.get(room, {})
        patterns = self.re_cache.get(room, [])
        permission = all(p.search(content) is None for p in patterns)
        if permission and room_state.get('remote_censor'):
            permission = await self.remote_censor(content)
        
        colors = room_state.get('user_danmaku_colors') or ['undefined']

        # internal send_async
        context.publish(
            topic_name=f'persistent://public/default/{room}',
            message=b'\x00\x00\x00',  # new danmaku
            serde_class_name='tagger.BytesIdentity',
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

    def process(self, input: bytes, context: Context):
        if context.get_current_message_topic_name() == 'persistent://public/default/state':
            room, state_str = json.loads(input.decode())
            room_state: Mapping[str, Any] = json.loads(state_str)
            self.state_cache[room] = {key: room_state[key] for key in ('remote_censor', 'user_danmaku_colors')}
            self.re_cache[room] = [re.compile('.*?'.join(list(keyword))) for keyword in room_state['keyword_blacklist']]
            return

        # WARNING: "current message" of context will be updated by main thread
        # should not get message info from context object in async functions
        asyncio.run_coroutine_threadsafe(self.tag(input, context), self.loop)
