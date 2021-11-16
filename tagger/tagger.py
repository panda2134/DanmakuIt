import time

import asyncio
from threading import Thread

from typing import Mapping

from aiohttp import ClientSession
from pulsar import Function, Context

def run_background_event_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def create_session():
    return ClientSession()

class CensorFunction(Function):
    def __init__(self):
        self.access_token = ''
        self.access_token_expiration = 0.0
        

        self.loop = asyncio.new_event_loop()
        thread = Thread(target=run_background_event_loop, args=(self.loop,), daemon=True)
        thread.start()

        self.session = asyncio.run_coroutine_threadsafe(create_session(), self.loop).result() # blocking
    
    def __del__(self):
        asyncio.run_coroutine_threadsafe(self.session.close(), self.loop).result() # blocking

    async def fetch_access_token(self):
        params = dict(
            grant_type='client_credentials',
            client_id='s7tl79bgMTtcuHkHZQ0WZp79',
            client_secret='D01hLswaLGzGOnPI6cCB8I0HCX9ljEGH'
        )
        async with self.session.post('https://aip.baidubce.com/oauth/2.0/token', params=params) as resp:
            resp_obj: Mapping = await resp.json(content_type=None)
            if 'error' in resp_obj:
                print('fetch access token fail')
                return
            self.access_token = resp_obj['access_token']
            # one day margin
            self.access_token_expiration = time.time() + resp_obj['expires_in'] - 86400

    async def censor(self, text: str):
        async with self.session.post('https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined',
                                params=dict(access_token=self.access_token),
                                data=f'text={text}',
                                headers={'content-type': 'application/x-www-form-urlencoded'}) as resp:
            resp_obj: Mapping = await resp.json(content_type=None)
            result: int = resp_obj.get('conclusionType', 4)
            return result == 1

    async def tag(self, input: str, context: Context):
        visibility = await self.censor(input)
        
        context.publish(
            topic_name='test',
            message='pass' if visibility else 'not pass'
        )
        print('complete tag')

    def process(self, input: str, context: Context):
        if self.access_token_expiration < time.time():
            asyncio.run_coroutine_threadsafe(self.fetch_access_token(), self.loop).result() # blocking
        asyncio.run_coroutine_threadsafe(self.tag(input, context), self.loop)