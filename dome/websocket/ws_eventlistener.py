from asyncio import get_event_loop
from websocket_v2 import listenEvents

loop = get_event_loop()
loop.run_until_complete(listenEvents())
loop.run_forever()