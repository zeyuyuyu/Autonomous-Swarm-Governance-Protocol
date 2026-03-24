import asyncio
import websockets
import json

async def handle_connection(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        if data['type'] == 'data_offer':
            await broadcast_data_offer(data)
        elif data['type'] == 'data_request':
            await fulfill_data_request(data, websocket)

async def broadcast_data_offer(data):
    offer = {
        'type': 'data_offer',
        'metadata': data['metadata'],
        'price': data['price']
    }
    async with websockets.connect('ws://localhost:8765') as websocket:
        await websocket.send(json.dumps(offer))

async def fulfill_data_request(data, requester):
    # Lookup data based on request metadata
    data_content = get_data_content(data['metadata'])
    response = {
        'type': 'data_response',
        'data': data_content
    }
    await requester.send(json.dumps(response))

def get_data_content(metadata):
    # Implement logic to retrieve data content
    return b'sample data content'

start_server = websockets.serve(handle_connection, 'localhost', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()