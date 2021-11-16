import asyncio
from aiohttp import ClientSession

async def main():
    async with ClientSession() as session:
        for _ in range(10):
            async with session.post('http://localhost:8000/room/3/port',
                                    data='<xml><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[测试内容]]></Content></xml>',
                                    headers={'Content-Type': 'application/xml'}) as resp:
                print(await resp.text())

if __name__ == '__main__':
    asyncio.run(main())