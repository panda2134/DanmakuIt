import asyncio
import json
from aiohttp import ClientSession
from tqdm import tqdm

async def main():
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
    <Content><![CDATA[我是你爹]]></Content>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    </xml>
    """
    async with ClientSession() as session:
        for _ in tqdm(range(3)):
            async with session.post('http://localhost:8000/room/3/port',
                                    data=data,
                                    headers={'Content-Type': 'application/xml'}) as resp:
                pass

        async with session.post('http://localhost:8000/setting/3', data=json.dumps({'remote_censor': True})) as resp:
            print(await resp.text())
        async with session.get('http://localhost:8080/admin/v3/functions/public/default/tagger/state/3') as resp:
            print(resp.status, await resp.text())
        async with session.post('http://localhost:8000/room/3/port',
                                data=data_not_pass,
                                headers={'Content-Type': 'application/xml'}) as resp:
            pass

        async with session.post('http://localhost:8000/room/3/port',
                                data=data,
                                headers={'Content-Type': 'application/xml'}) as resp:
            pass

if __name__ == '__main__':
    asyncio.run(main())