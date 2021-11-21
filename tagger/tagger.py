import asyncio, threading
import time, os, binascii
import json


from typing import Mapping, Optional

from aiohttp import ClientSession
from pulsar import Function, Context, SerDe

class BytesIdentity(SerDe): # Real Identity, not str()
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
        self.access_token_refetch_margin = 2e5 # sec
        self.remote_censor_max_retry_times = 10
        
        self.loop = loop = asyncio.new_event_loop()
        def run_background_event_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()
        threading.Thread(target=run_background_event_loop, daemon=True).start()

        async def create_session():
            return ClientSession()
        self.session = asyncio.run_coroutine_threadsafe(create_session(), loop).result() # blocking

        asyncio.run_coroutine_threadsafe(self.fetch_access_token(), loop) # infinite loop fetch access token

        self.state_cache: Mapping[str, dict] = {}
    
    def __del__(self):
        asyncio.run_coroutine_threadsafe(self.session.close(), self.loop).result() # blocking

    async def fetch_access_token(self):
        params = dict(
            grant_type='client_credentials',
            client_id='s7tl79bgMTtcuHkHZQ0WZp79',
            client_secret='D01hLswaLGzGOnPI6cCB8I0HCX9ljEGH'
        )
        while True:
            async with self.session.post('https://aip.baidubce.com/oauth/2.0/token', params=params) as resp:
                resp_obj: Mapping = await resp.json(content_type=None)
                if 'error' not in resp_obj:
                    self.access_token = resp_obj['access_token']
                    delta_time = float(resp_obj['expires_in'])
                    self.access_token_expiration = time.time() + delta_time
                    await asyncio.sleep(max(5.0, delta_time - self.access_token_refetch_margin))
                else:
                    print('fetch access token fail')
                    await asyncio.sleep(5.0) # retry 5s

    async def remote_censor(self, text: str, retry_times: int = 0):
        while self.access_token_expiration < time.time():
            await asyncio.sleep(1.0) # blocking until new access token has been fetched

        async with self.session.post('https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined',
                                params=dict(access_token=self.access_token),
                                data=f'text={text}',
                                headers={'content-type': 'application/x-www-form-urlencoded'}) as resp:
            resp_obj: Mapping = await resp.json(content_type=None)
            result: Optional[int] = resp_obj.get('conclusionType')
            if result is not None:
                return (result == 1)
            
            if resp_obj.get('error_code') != 18 or retry_times >= self.remote_censor_max_retry_times:
                return False
            
            # qps limit, retry after 1 ~ 3.55 sec
            await asyncio.sleep(1 + int.from_bytes(os.urandom(1), 'little') * 0.01)
            return await self.remote_censor(text, retry_times + 1)

    async def tag(self, input: bytes, context: Context):
        obj: Mapping[str, str] = json.loads(input.decode())
        
        content = obj['content']
        room = obj['room']
    
        room_state = self.state_cache.get(room, {})

        permission = True # TODO: room specific censor
        if permission and room_state.get('remote_censor'):
            permission = await self.remote_censor(content)

        # internal send_async
        context.publish(
            topic_name=f'persistent://public/default/{room}',
            message=b'\x00\x00\x00', # new danmaku
            serde_class_name='tagger.BytesIdentity',
            properties=dict(
                content=content,
                id=binascii.b2a_base64(os.urandom(24), newline=False).decode(),
                sender=obj['sender'],
                permission='1' if permission else '0', # properties must be string
                color=room_state.get('color', 'undefined'),
                size=room_state.get('size', '16pt'),
                pos=room_state.get('pos', 'rightleft')
            )
        )

    def process(self, input: bytes, context: Context):
        if context.get_current_message_topic_name() == 'persistent://public/default/state':
            arr = json.loads(input.decode())
            room: str = arr[0]
            method: str = arr[1]
            if method == 'replace':
                state_str: str = arr[2]
                self.state_cache[room] = json.loads(state_str)
                context.put_state(room, state_str)
                return
            if method == 'load':
                state_str: str = context.get_state(room)
                self.state_cache[room] = json.loads(state_str)
                return
            # invalid method!
            print(arr)
            return
        
        # WARNING: "current message" of context will be updated by main thread
        # should not get message info from context object in async functions
        asyncio.run_coroutine_threadsafe(self.tag(input, context), self.loop)