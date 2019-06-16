from multiprocessing import Process
import asyncio
import time

# from dome.util.KnowledgeGraph import KnowledgeGraph
from dome.lib.observable import Observable
from dome.lib.state import BaseState
from dome.websocket.HAService import call

from dome.db.graph import Graph, DOME
from dome.automations.AutomationUtil import verifyTrigger, gatherServiceInfo

# from dome.config import DOME_NAMESPACE as DOME
from rdflib.namespace import RDFS

class State(BaseState):
    WAITING_READ_VALIDATE = (1, 'WAITING READ VALIDATE')
    VALIDATING = (2, 'VALIDATING')
    WAITING_READ_PREPARE = (3, 'WAITING READ PREPARE')
    PREPARE = (4, 'PREPARING')
    SERVICE_CALL = (5, 'CALLING SERVICE')
    ABORTED = (0, 'ABORTED')

class Resolver(Process, Observable):
    state = State()

    def __init__(self, dome, automation_id):
        Process.__init__(self)
        Observable.__init__(self)
        self.dome = dome
        self.kb_readable = dome.graph_readable_event
        self.automation_id = automation_id
    
    def run(self):
        print('Resolver Running')
        # Wait until the kb is readable and validate the trigger
        self.update(State.WAITING_READ_VALIDATE)
        self.kb_readable.wait()
        self.update(State.VALIDATING)
        main_trigger = Graph.getModel().get_target(self.automation_id, DOME.triggeredby)
        valid = verifyTrigger(main_trigger)
        if (not valid):
            self.update(State.ABORTED)
            return
        
        # # Wait until the kb is readable again and prepare
        self.update(State.WAITING_READ_PREPARE)
        self.kb_readable.wait()
        self.update(State.PREPARE)
        services = gatherServiceInfo(self.automation_id)

        # Call the HA service through the websocket
        self.update(State.SERVICE_CALL)
        loop = asyncio.get_event_loop()
        tasks = []
        for service in services:
            tasks.append(asyncio.ensure_future(call(
                service['ha_type'], 
                service['service'], 
                service['ha_name']
            )))
        loop.run_until_complete(asyncio.gather(*tasks))

        self.update(State.FINISHED)
    
    def update(self, state):
        self.state.update(state)
        self.notify('[{}] {}'.format(self.name, self.state))