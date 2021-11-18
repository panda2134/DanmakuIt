import asyncio
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
    async with ClientSession() as session:
        for _ in tqdm(range(10000)):
            async with session.post('http://localhost:8000/room/3/port',
                                    data=data,
                                    headers={'Content-Type': 'application/xml'}) as resp:
                pass

if __name__ == '__main__':
    asyncio.run(main())