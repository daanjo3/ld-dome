import asyncio
import json
import os

from websockets import connect

from dome.config import *

from dome.parser.parser_direct import parseEntityDump, parseEvent

class Observable(object):
    def __init__(self):
        self.callbacks = []
    
    def register(self, callback):
        self.callbacks.append(callback)
    
    def unregister(self, callback):
        self.callbacks.remove(callback)
    
    def notify(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)

async def loadEntities():
    async with connect('ws://192.168.1.100:8123/api/websocket') as websocket:
        auth = json.dumps({'type': 'auth', 'access_token': ACCESS_TOKEN})
        await websocket.send(auth)

        get_entities = json.dumps({'id': 1, 'type': 'get_states'})
        await websocket.send(get_entities)

        while True:
            message_raw = await websocket.recv()
            message = json.loads(message_raw)

            if (message['type'] == 'result' and message['id'] == 1):
                parseEntityDump(message['result'])
                return

class WSEventListener(Observable):
    async def listenEvents(self):
        async with connect('ws://192.168.1.100:8123/api/websocket') as websocket:
            auth = json.dumps({'type': 'auth', 'access_token': ACCESS_TOKEN})
            await websocket.send(auth)

            subscribe = json.dumps({'id': 1, 'type': 'subscribe_events', 'event_type': 'state_changed'})
            await websocket.send(subscribe)

            while True:
                message_raw = await websocket.recv()
                message = json.loads(message_raw)

                if (message['type'] == 'event' and message['id'] == 1):
                    self.notify('--- Parsing event ---')
                    parseEvent(message['event']['data'])
                    self.notify('--- Finished event parsing ---')

async def callService(domain, service, entity_id):
    async with connect('ws://192.168.1.100:8123/api/websocket') as websocket:
        auth = json.dumps({'type': 'auth', 'access_token': ACCESS_TOKEN})
        await websocket.send(auth)

        call = json.dumps({
            'id': 1,
            'type': 'call_service',
            'domain': domain,
            'service': service,
            'service_data': {'entity_id': entity_id}})
        await websocket.send(call)

        while True:
            message_raw = await websocket.recv()
            message = json.loads(message_raw)

            if (message['type'] == 'result' and message['id'] == 1):
                if (message['success']):
                    print('SERVICE CALL SUCCESSFUL')
                else:
                    print('SERVICE CALL FAILED')
                return

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(loadEntities())
    # loop.run_until_complete(listenEvents())
    # loop.run_until_complete(callService('switch', 'turn_off', 'switch.sonoff_2'))

    # loop.run_forever()
    loop.close()
    print('loop closed')