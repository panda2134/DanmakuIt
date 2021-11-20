import json
import websocket


    


ws = websocket.create_connection('ws://localhost:8080/ws/v2/consumer/persistent/public/default/3/testsub')
while True:
    msg = json.loads(ws.recv())
    print(msg['properties'])
    # Acknowledge successful processing
    ws.send(json.dumps({'messageId' : msg['messageId']}))