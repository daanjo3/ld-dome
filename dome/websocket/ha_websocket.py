#!/usr/bin/python3
#
# Copyright (c) 2017-2018, Fabian Affolter <fabian@affolter-engineering.ch>
# Released under the ASL 2.0 license. See LICENSE.md file for details.
#

# Built-in modules
import asyncio
import json
import os
import shutil

# Installed modules
import asyncws

# Custom modules
from dome.config import *


async def main():
    """Simple WebSocket client for Home Assistant."""
    # websocket = await asyncws.connect('ws://localhost:8000/api/websocket')
    websocket = await asyncws.connect('ws://192.168.1.100:8123/api/websocket')

    await websocket.send(json.dumps(
        {'type': 'auth',
         'access_token': ACCESS_TOKEN}
    ))

    await websocket.send(json.dumps(
        {'id': 1, 'type': 'subscribe_events', 'event_type': 'state_changed'}
    ))

    # Request the states of all devices
    await websocket.send(json.dumps(
        {
            "id": 2,
            "type": "get_states"
        }
    ))

    # Request information on the current configuration
    await websocket.send(json.dumps(
        {
            "id": 3,
            "type": "get_config"
        }
    ))

    # Request information on the available services
    await websocket.send(json.dumps(
        {
            "id": 4,
            "type": "get_services"
        }
    ))

    # Boolean to track whether all requests have been fulfilled
    recv_config, recv_dev, recv_service = False, False, False
    while True:
        message = await websocket.recv()
        if message is None:
            break
        
        jmessage = json.loads(message)
        # We need the a result, that is not empty, and is the answer to query with id=2
        if (jmessage['type'] == 'result' and jmessage['result']):
            if (jmessage['id'] == 2):
                writeDevices(jmessage, WEBSOCKET_OUT_DEVICE)
                recv_dev = True
            if (jmessage['id'] == 3):
                with open(WEBSOCKET_OUT_CONFIG, 'w') as f:
                    json.dump(jmessage, f, indent=2)
                recv_config = True
            if (jmessage['id'] == 4):
                with open(WEBSOCKET_OUT_SERVICE, 'w') as f:
                    json.dump(jmessage, f, indent=2)
                recv_service = True
        
        # Check whether all requests have been fulfilled
        if (recv_dev and recv_config and recv_service):
            return

def writeDevices(data, path):
    for r in data['result']:
        if r['entity_id'] in DEVICE_WHITELIST:
            filepath = path + r['entity_id']
            with open(filepath, 'w') as f:
                json.dump(r, f, indent=2)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()