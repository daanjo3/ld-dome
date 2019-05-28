import asyncio
import time
import threading

from dome.websocket import socket_loader, socket_service, socket_update

from dome.util.kb import KnowledgeGraph
from dome.parser.parser import parseEvent

class Dome():
    ws_event_loop = None
    parser_event_loop = None

    def __init__(self):
        self.graph = KnowledgeGraph()
        self.graph.register(self.graphUpdate)
        self.statelistener = socket_update.HAStateListener()
        self.parser_event_loop = asyncio.new_event_loop()
    
    def graphUpdate(self, update_data):
        print(update_data)
        # for k in update_data.keys():
            # print(k, update_data[k])

    def parseEventUpdate(self, event_data):
        pass
        
    async def startStateListener(self):
        self.ws_event_loop = asyncio.new_event_loop()
        ws_event_thread = threading.Thread(
            target=self.statelistener.start,
            args=(self.ws_event_loop,))
        ws_event_thread.start()
        self.ws_event_loop.call_soon_threadsafe(
            self.statelistener.register, 
            self.parseEventUpdate
        )
    
    async def start(self):
        print('Loading entities')
        await socket_loader.load()
        print('Starting state listener')
        await self.startStateListener()
        print('Started state listener')
        

if __name__ == '__main__':
    dome = Dome()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dome.start())
    loop.close()