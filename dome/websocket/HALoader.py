import asyncio
import json

from websockets import connect

from dome.config import *
from dome.parser.ParserService import Origin

# Async function that loads all entity data and queues it in the parser
async def load(queue):
    async with connect('ws://192.168.1.100:8123/api/websocket') as websocket:
        auth = json.dumps({'type': 'auth', 'access_token': ACCESS_TOKEN})
        await websocket.send(auth)

        get_entities = json.dumps({'id': 1, 'type': 'get_states'})
        await websocket.send(get_entities)

        while True:
            message_raw = await websocket.recv()
            message = json.loads(message_raw)

            if (message['type'] == 'result' and message['id'] == 1):
                queue.put((Origin.HA_LOADER, message['result']))
                return

if __name__ == "__main__":
    from multiprocessing import Manager
    manager = Manager()
    queue = manager.Queue()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load(queue))
    print(queue.get(block=True))