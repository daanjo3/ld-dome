import asyncio
import json

from websockets import connect
from multiprocessing import Process

from dome.config import *
from dome.lib.observable import Observable
from dome.parser.ParserService import ParserService

# Class used for continuous HA-updates to the the knowledge base
class HAUpdater(Process, Observable):

    def __init__(self, queue):
        self.queue = queue
        Process.__init__(self)
        Observable.__init__(self)

    def run(self):
        loop = asyncio.get_event_loop()
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
                    self.queue.put((ParserService.Origin.HA_UPDATER, message['event']['data']['new_state']))
                    kb_prop = None
                    # kb_prop = parseEvent(message['event']['data'])
                    if (kb_prop is not None):
                        pass
                        # self.queue.put(message['event']['data'])
                        # self.notify({
                        #     'domain': 'websocket',
                        #     'op': 'update',
                        #     'prop': kb_prop,
                        #     'data': message['event']['data']
                        # })