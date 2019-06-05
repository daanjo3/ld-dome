import asyncio
import json

from websockets import connect

from dome.config import *
from dome.lib.observable import Observable
from dome.parser.parser import parseEvent

class HAStateListener(Observable):

    def __init__(self):
        super().__init__()

    def start(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.listen())
        loop.run_forever()

    async def listen(self):
        async with connect('ws://192.168.1.100:8123/api/websocket') as websocket:
            auth = json.dumps({'type': 'auth', 'access_token': ACCESS_TOKEN})
            await websocket.send(auth)

            subscribe = json.dumps({'id': 1, 'type': 'subscribe_events', 'event_type': 'state_changed'})
            await websocket.send(subscribe)

            while True:
                message_raw = await websocket.recv()
                message = json.loads(message_raw)

                if (message['type'] == 'event' and message['id'] == 1):
                    kb_prop = parseEvent(message['event']['data'])
                    if (kb_prop is not None):
                        self.notify({
                            'domain': 'websocket',
                            'op': 'update',
                            'prop': kb_prop,
                            'data': message['event']['data']
                        })

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(listen())
    loop.run_forever()
    loop.close()
    print('loop closed')