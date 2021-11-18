import time, random
import asyncio, threading
import json

from typing import Any, Mapping

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

        self.state_cache: Mapping[str, bytes] = {}
    
    def __del__(self):
        asyncio.run_coroutine_threadsafe(self.session.close(), self.loop).result() # blocking

    async def fetch_access_token(self):
        params = dict(
            grant_type='client_credentials',
            client_id='***REMOVED***',
            client_secret='***REMOVED***'
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
            result: int = resp_obj.get('conclusionType')
            if result is not None:
                return (result == 1)
            
            if resp_obj.get('error_code') != 18 or retry_times >= self.remote_censor_max_retry_times:
                return False
            
            # qps limit, retry after 1 ~ 3 sec
            await asyncio.sleep(1.0 + random.random() * 2.0)
            return await self.remote_censor(text, retry_times + 1)

    async def tag(self, input: bytes, context: Context):
        obj: Mapping[str, str] = json.loads(input.decode())
        
        content = obj['content']
        sender = obj['sender']
        room = obj['room']
        room_state_binary = self.state_cache.get(room)
        room_state: Mapping[str, Any] = json.loads(room_state_binary.decode()) if room_state_binary is not None else {}
        visibility = True # TODO: room specific censor
        if visibility and room_state.get('remote_censor'):
            visibility = await self.remote_censor(context)
        # internal send_async
        context.publish(
            topic_name=f'persistent://public/default/{room}',
            message=json.dumps(
                dict(
                    content=content,
                    sender=sender,
                    visibility=visibility
                ),
                ensure_ascii=False
            ).encode()
        )

    def process(self, input: bytes, context: Context):
        if context.get_current_message_topic_name() == 'persistent://public/default/state_update':
            # notify state update
            room = input.decode()
            self.state_cache[room] = context.get_state(room)
            return
        
        # WARNING: "current message" of context will be updated by main thread
        # should not get message info from context object in async functions
        asyncio.run_coroutine_threadsafe(self.tag(input, context), self.loop)