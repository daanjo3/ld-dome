from multiprocessing import Process

from dome.lib.observable import Observable
from dome.lib.state import BaseState
from dome.lib.validate import validEntity

# from dome.util.KnowledgeGraph import KnowledgeGraph

import dome.config as config
DOME = config.DOME_NAMESPACE

# Custom exception for the parser
class ParseException(Exception):
        pass
    
class State(BaseState):
    WAITING_WRITE = (3, 'WAITING_WRITE')
    WRITING = (4, 'WRITING')

class ParseType:
    IGNORE = 0
    NEW = 1
    UPDATE = 2

class WParser(Process, Observable):
    
    # Class variables
    state = State()
    raw_entity = None
    prepared_entity = None

    def __init__(self, dome, payload, kb_writelock):
        Process.__init__(self)
        Observable.__init__(self)
        self.raw_entity = payload
        self.kb_readable = dome.graph_readable_event
        self.kb_writelock = kb_writelock
        self.outqueue = dome.automation_queue
    
    def run(self):
        # Make the kb unreadable and acquire a lock to write
        self.update(State.WAITING_WRITE)
        self.kb_writelock.acquire()
        self.kb_readable.clear()

        self.update(State.WRITING)
        self.write()

        # Release the lock and set the readable event
        self.kb_writelock.release()
        self.kb_readable.set()
        self.update(State.FINISHED)

    # Write function that either write an update or new addition to the knowledge base
    def write(self):
        prop_id = self.raw_entity['id']
        last_updated = self.raw_entity['last_updated']
        state = self.raw_entity['state']

        KnowledgeGraph.modify_literal(prop_id, DOME.last_updated, last_updated)
        KnowledgeGraph.modify_literal(prop_id, DOME.value, state)
        self.outqueue.put(prop_id)

        
    def update(self, state):
        self.state.update(state)
        self.notify('[{}] {}'.format(self.name, self.state))