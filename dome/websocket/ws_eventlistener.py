from asyncio import get_event_loop
from websocket_v2 import WSEventListener

def printCallback(*args, **kwargs):
    for param in args:
        print(param)

wsel = WSEventListener()
wsel.register(printCallback)

loop = get_event_loop()
loop.run_until_complete(wsel.listenEvents())
loop.run_forever()