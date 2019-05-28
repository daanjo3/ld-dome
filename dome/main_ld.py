import asyncio
import time
import threading

import dome.websocket.websocket_v2 as ws
from dome.util.kb import KnowledgeGraph
from dome.parser.parser_direct import parseEvent

class Dome():
    ws_event_loop = None
    parser_event_loop = None

    def __init__(self):
        self.graph = KnowledgeGraph()
        self.eventLoader = ws.WSEventListener()
        self.parser_event_loop = asyncio.new_event_loop()
    
    def parseEventUpdate(self, event_data):
        for k in event_data.keys():
            print(k)
        
    async def startEventLoader(self):
        self.ws_event_loop = asyncio.new_event_loop()
        ws_event_thread = threading.Thread(
            target=self.eventLoader.start,
            args=(self.ws_event_loop,))
        ws_event_thread.start()
        self.ws_event_loop.call_soon_threadsafe(
            self.eventLoader.register, 
            self.parseEventUpdate
        )
    
    async def start(self):
        print('Entering start')
        print('Loading entities')
        await ws.loadEntities()
        print('Starting eventLoader')
        await self.startEventLoader()
        print('Started eventLoader')
        

if __name__ == '__main__':
    dome = Dome()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dome.start())
    loop.close()