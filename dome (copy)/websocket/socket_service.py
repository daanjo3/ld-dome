import asyncio
import json

from websockets import connect

from dome.config import *

async def call(domain, service, entity_id):
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
    print('Running callService')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(call('switch', 'turn_off', 'switch.sonoff_2'))
    loop.close()
    print('loop closed')