# built-in import
from multiprocessing import Process
from time import time, sleep

# DomeLD import
from dome.lib.observable import Observable
from dome.lib.state import BaseState
from dome.lib.validate import validEntity
from dome.db.graph import Graph
from dome.config import DOME, DOME_DATA, ACTUATORS
from RDF import RedlandError

# Custom exception for the parser
class ParseException(Exception):
        pass
    
class State(BaseState):
    WAITING_READ = (1, 'WAITING READ')
    PREPARING = (2, 'PREPARING')
    PREPARING_FAILED = (20, 'PREPARING_FAILED_RETRY')
    WAITING_WRITE = (3, 'WAITING_WRITE')
    WRITING = (4, 'WRITING')
    FAILED = (5, 'PARSER FAILED')

class ParseType:
    IGNORE = 0
    NEW = 1
    UPDATE = 2

class HAParser(Process, Observable):
    
    # Class variables
    state = State()
    raw_entity = None
    prepared_entity = None

    def __init__(self, dome, payload, kb_writelock, outqueue=None):
        Process.__init__(self)
        Observable.__init__(self)
        self.raw_entity = payload
        self.kb_readable = dome.graph_readable_event
        self.kb_writelock = kb_writelock
        self.outqueue = outqueue
        self.bm_queue = dome.bm_queue
    
    def run(self):
        self.bm_queue.put((self.name, 'start', time()))
        # Wait until the kb is readable and prepare the data
        prepared = False
        while(not prepared):
            try:
                self.update(State.WAITING_READ)
                self.kb_readable.wait()
                self.update(State.PREPARING)
                prepared = self.prepare()
            except RedlandError:
                self.update(State.PREPARING_FAILED)
                sleep(0.3)

        # Make the kb unreadable and acquire a lock to write
        try:
            self.update(State.WAITING_WRITE)
            self.kb_writelock.acquire()
            self.kb_readable.clear()

            self.update(State.WRITING)
            if (self.prepared_entity['parse'] == ParseType.UPDATE): self.writeUpdate()
            if (self.prepared_entity['parse'] == ParseType.NEW): self.writeCreate()
        except RedlandError:
            self.update(State.FAILED)

        # Release the lock and set the readable event
        self.kb_writelock.release()
        self.kb_readable.set()
        self.update(State.FINISHED)

        self.bm_queue.put((self.name, 'stop', time()))

    def writeUpdate(self):
        data = self.prepared_entity['data']
        prop_ref = data['id']
        Graph.updateStatement(prop_ref, DOME.last_changed, data['last_changed'])
        Graph.updateStatement(prop_ref, DOME.last_updated, data['last_updated'])
        Graph.updateStatement(prop_ref, DOME.value, data['state'])
        if (self.outqueue):
            self.outqueue.put(str(prop_ref))
   
    def writeCreate(self):
        dev = self.prepared_entity['data']['device']
        prop = self.prepared_entity['data']['property']
        prop_ref = Graph.addProperty(
            prop['label'],
            prop['state'], 
            prop['last_updated'],
            prop['last_changed']
        )
        Graph.addDevice(
            dev['label'],
            dev['actuator'],
            prop_ref, 
            dev['ha_name'],
            dev['ha_type']
        )
        if (self.outqueue):
            self.outqueue.put(str(prop_ref))
    
    # Main method used to prepare the data of the parser
    def prepare(self):
        prepared_entity = {}
        self.ha_name = self.raw_entity['entity_id']
        self.ha_type = self.ha_name.split('.')[0]

        if (validEntity(self.ha_name)):
            self.device_ref = Graph.getModel().get_source(DOME.ha_name, self.ha_name)

            if (self.device_ref is not None):
                # Parse the data as update
                self.prepareUpdate()   
            else:
                # Parse the data as new info
                self.prepareNew()
        else:
            self.prepared_entity = {
                'entity': self.raw_entity['entity_id'],
                'parse': ParseType.IGNORE,
                'data': None
            }
        return True

    def prepareUpdate(self):                
        # Get the device property
        prop_ref = Graph.getModel().get_target(self.device_ref, DOME.actuates) or Graph.getModel().get_target(self.device_ref, DOME.observes)        
        if (prop_ref is None): raise ParseException
        
        self.prepared_entity = {
            'entity': self.raw_entity['entity_id'],
            'parse': ParseType.UPDATE,
            'data': {
                'id': prop_ref,
                'last_changed': self.raw_entity['last_changed'],
                'last_updated': self.raw_entity['last_updated'],
                'state': self.raw_entity['state']
            }
        }
    
    # Prepare the data for a new addition to the graph
    def prepareNew(self):
        label = None
        try:
            label = self.raw_entity['attributes']['friendly_name']
        except KeyError:
            label = self.raw_entity['entity_id']

        self.prepared_entity = {
            'entity': self.raw_entity['entity_id'],
            'parse': ParseType.NEW,
            'data': {
                'device': {
                    'label': label,
                    'actuator': self.ha_type in ACTUATORS,
                    'ha_name': self.ha_name,
                    'ha_type': self.ha_type
                },
                'property': {
                    'label': self.raw_entity['entity_id'],
                    'state': self.raw_entity['state'],
                    'last_updated': self.raw_entity['last_updated'],
                    'last_changed': self.raw_entity['last_changed']
                }
            }
        }
    
    def update(self, state):
        self.state.update(state)
        self.notify('[{}] {}'.format(self.name, self.state))