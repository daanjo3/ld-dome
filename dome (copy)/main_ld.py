import asyncio
import time
import threading

from rdflib.namespace import RDFS

from dome.websocket import socket_loader, socket_service, socket_update
from dome.websocket.socket_service import call

from dome.config import DOME_NAMESPACE as DOME
from dome.util.kb import KnowledgeGraph
from dome.parser.parser import parseEvent
from dome.automation_resolver import AutomationResolver, test_create_automation

class Dome():
    ws_event_loop = None
    ar_event_loop = None
    parser_event_loop = None

    def __init__(self):
        KnowledgeGraph.register(self.graphUpdate)
        AutomationResolver.register(self.automationResolved)
        self.statelistener = socket_update.HAStateListener()
        self.parser_event_loop = asyncio.new_event_loop()
    
    # ------  Event listeners  ------
    def graphUpdate(self, graph_update):
        print('[MAIN] Received graph update')
        etype = graph_update['type']
        data = graph_update['data']
        if (etype == str(DOME.Automation)):
            AutomationResolver.add(data)

    def haUpdate(self, ha_update):
        print('[MAIN] Received home assistant update for prop {}'.format(ha_update['prop']))
        AutomationResolver.onUpdate(ha_update['prop'])
    
    def automationResolved(self, service_calls):
        print('[MAIN] Automation resolved, calling services')
        for scall in service_calls:
            loop = asyncio.get_event_loop()
            task = loop.create_task(call(scall['domain'], scall['service'], scall['entity_id']))
    
    # -----  Loaders  ------
    def startStateListener(self):
        print('[MAIN] Starting state listener')
        self.ws_event_loop = asyncio.new_event_loop()
        ws_event_thread = threading.Thread(
            target=self.statelistener.start,
            args=(self.ws_event_loop,))
        ws_event_thread.start()
        self.ws_event_loop.call_soon_threadsafe(
            self.statelistener.register, 
            self.haUpdate
        )
        print('[MAIN] Started state listener')
    
    async def start(self):
        # print('[MAIN] Loading entities')
        # await socket_loader.load()
        self.startStateListener()

        print('[MAIN] Creating test automation')
        automation_created = test_create_automation()
        if (not automation_created):
            automations = KnowledgeGraph.get_entities_by_type(DOME.Automation, mode=2)
            for automation in automations:
                AutomationResolver.add(automation)
        

if __name__ == '__main__':
    dome = Dome()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dome.start())
    loop.close()