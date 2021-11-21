import asyncio
import json
from aiohttp import ClientSession
from tqdm import tqdm

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
censor = False

controller = 'https://se-srv.panda2134.site'
pulsar = 'https://se-srv2.panda2134.site'

async def main():
    async with ClientSession() as session:
        if perf_test:
            for _ in tqdm(range(100)):
                async with session.post(f'{controller}/room/3/port',
                                        data=data,
                                        headers={'Content-Type': 'application/xml'}) as resp:
                    pass

        async with session.post(f'{controller}/setting/3', data=json.dumps({'remote_censor': censor})) as resp:
            print(await resp.text())
            await asyncio.sleep(3)
        async with session.get(f'{pulsar}/admin/v3/functions/public/default/tagger/state/3') as resp:
            print(resp.status, await resp.text())

        async with session.post(f'{controller}/room/3/port',
                                data=data_not_pass,
                                headers={'Content-Type': 'application/xml'}) as resp:
            print(await resp.text())

        async with session.post(f'{controller}/room/3/port',
                                data=data,
                                headers={'Content-Type': 'application/xml'}) as resp:
            print(await resp.text())

if __name__ == '__main__':
    if type(asyncio.get_event_loop_policy()) == asyncio.WindowsProactorEventLoopPolicy:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())