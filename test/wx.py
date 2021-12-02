import asyncio
import platform
import json
from httpx import AsyncClient
from tqdm import tqdm
from conf import room_id, room_passcode

data = """
<xml>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[测试内容]]></Content>
<FromUserName><![CDATA[fromUser]]></FromUserName>
</xml>
"""
data_not_pass = """
<xml>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[习近平]]></Content>
<FromUserName><![CDATA[fromUser]]></FromUserName>
</xml>
"""

perf_test = False
set_state = False
censor = True

domain = 'http://localhost:8000'  # 'https://se-srv.panda2134.site'


async def main():
    async with AsyncClient() as client:
        if perf_test:
            for _ in tqdm(range(100)):
                await client.post(f'{domain}/port/{room_id}',
                                  data=data,
                                  headers={'Content-Type': 'application/xml'})

        if set_state:
            resp = await client.post(f'{domain}/setting/{room_id}', data=json.dumps({'remote_censor': censor}))
            print(resp.text)
            await asyncio.sleep(3)

        # resp = await client.post(f'{domain}/room/{room_id}')
        # print(resp.text)

        # print('Fetching room settings')
        # resp = await client.get(f'{domain}/setting/{room_id}')
        # print(resp.text)

        print('Sending message - Pass')
        resp = await client.post(f'{domain}/port/{room_id}',
                                 data=data,
                                 headers={'Content-Type': 'application/xml'})
        print(resp.text)

        print('Sending message - Fail')
        resp = await client.post(f'{domain}/port/{room_id}',
                                 data=data_not_pass,
                                 headers={'Content-Type': 'application/xml'})
        print(resp.text)

if __name__ == '__main__':
    if platform.system() == 'Windows' and type(asyncio.get_event_loop_policy()) == asyncio.WindowsProactorEventLoopPolicy:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
