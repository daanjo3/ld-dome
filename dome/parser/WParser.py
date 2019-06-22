from multiprocessing import Process
from time import time

from dome.lib.observable import Observable
from dome.lib.state import BaseState

from dome.db.graph import Graph
from RDF import Uri, RedlandError
from dome.config import DOME

# Custom exception for the parser
class ParseException(Exception):
        pass
    
class State(BaseState):
    WAITING_WRITE = (3, 'WAITING_WRITE')
    WRITING = (4, 'WRITING')
    FAILED = (5, 'PARSER FAILED')

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
        self.bm_queue = dome.bm_queue
    
    def run(self):
        self.bm_queue.put((self.name, 'start', time()))
        # Make the kb unreadable and acquire a lock to write
        try:
            self.update(State.WAITING_WRITE)
            self.kb_writelock.acquire()
            self.kb_readable.clear()

            self.update(State.WRITING)
            self.write()
        except RedlandError:
            self.update(State.FAILED)
        
        # Release the lock and set the readable event
        self.update(State.FINISHED)
        self.kb_writelock.release()
        self.kb_readable.set()

        self.bm_queue.put((self.name, 'stop', time()))

    # Write function that either write an update or new addition to the knowledge base
    def write(self):
        prop_id = Uri(self.raw_entity['id'])
        last_updated = self.raw_entity['last_updated']
        state = self.raw_entity['state']
        print('[WPARSER] Updated {} to state {}'.format(str(prop_id), state))

        Graph.updateStatement(prop_id, DOME.last_updated, last_updated)
        Graph.updateStatement(prop_id, DOME.value, str(state))
        self.outqueue.put(str(prop_id))

        
    def update(self, state):
        self.state.update(state)
        self.notify('[{}] {}'.format(self.name, self.state))