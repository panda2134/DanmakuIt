import asyncio
from httpx import AsyncClient
from tqdm import tqdm
from conf import room_id

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

domain = 'https://danmakuit.panda2134.site'  # 'https://se-srv.panda2134.site'


async def main():
    async with AsyncClient() as client:
        if perf_test:
            for _ in tqdm(range(100)):
                await client.post(f'{domain}/port/{room_id}',
                                  data=data,
                                  headers={'Content-Type': 'application/xml'})

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
    if type(asyncio.get_event_loop_policy()) == getattr(asyncio, 'WindowsProactorEventLoopPolicy', None):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
