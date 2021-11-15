from hashlib import sha1
from xml.etree import ElementTree

from aiohttp import web
import pulsar
pulsar_client = pulsar.Client('pulsar://pulsar:6650')

routes = web.RouteTableDef()

async def get_room_token(room_id: str):
    return 'placeholder'

@routes.get('/room/{id}/port')
async def room_port_get(request: web.Request):
    room_id = request.match_info['id']
    token = await get_room_token(room_id)

    query = request.query
    timestamp = query.get('timestamp', '')
    nonce = query.get('nonce', '')
    signature = query.get('signature', '')

    tmpArr = [token, timestamp, nonce]
    tmpArr.sort()
    hash = sha1()
    hash.update(''.join(tmpArr).encode('utf-8'))
    if (hash.hexdigest() == signature):
        echostr = query.get('echostr', '')
        return web.Response(text=echostr)
    
    return web.Response(text='Wrong signature!')

def send_raw_callback(res, msg_id):
    pass

@routes.post('/room/{id}/port')
async def room_port_post(request: web.Request):
    room_id = request.match_info['id']
    root = ElementTree.fromstring(await request.text())
    data = {el.tag: el.text for el in root}
    content = data.get('Content', '')

    producer = pulsar_client.create_producer('raw')
    producer.send_async(content=content.encode('utf-8'), callback=send_raw_callback)
    return web.Response(text='success')

@routes.get('/')
async def room_port_post(request: web.Request):
    reader = pulsar_client.create_reader('raw', start_message_id=pulsar.MessageId.earliest)
    msgs = []
    while reader.has_message_available():
        # receive/read_next will block whole server if there is no message available
        msg: bytes = reader.read_next().data()
        msgs.append(msg.decode('utf-8'))
    
    return web.Response(text=str[msgs])



app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app, port=8000)
