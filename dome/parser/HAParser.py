from multiprocessing import Process

from dome.lib.observable import Observable
from dome.lib.state import BaseState
from dome.lib.validate import validEntity

from dome.util.KnowledgeGraph import KnowledgeGraph

import dome.config as config
DOME = config.DOME_NAMESPACE

# Custom exception for the parser
class ParseException(Exception):
        pass
    
class State(BaseState):
    WAITING_READ = (1, 'WAITING READ')
    PREPARING = (2, 'PREPARING')
    WAITING_WRITE = (3, 'WAITING_WRITE')
    WRITING = (4, 'WRITING')

class ParseType:
    IGNORE = 0
    NEW = 1
    UPDATE = 2

class HAParser(Process, Observable):
    
    # Class variables
    state = State()
    raw_entity = None
    prepared_entity = None

    def __init__(self, payload, kb_readable, kb_writelock, outqueue):
        Process.__init__(self)
        Observable.__init__(self)
        self.raw_entity = payload
        self.kb_readable = kb_readable
        self.kb_writelock = kb_writelock
        self.outqueue = outqueue
    
    def run(self):
        # Wait until the kb is readable and prepare the data
        self.update(State.WAITING_READ)
        self.kb_readable.wait()
        self.update(State.PREPARING)
        self.prepare()

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
        if(self.prepared_entity['parse'] == ParseType.UPDATE):
            data = self.prepared_entity['data']
            KnowledgeGraph.modify_literal(data['id'], DOME.last_changed, data['last_changed'])
            KnowledgeGraph.modify_literal(data['id'], DOME.last_updated, data['last_updated'])
            KnowledgeGraph.modify_literal(data['id'], DOME.value, data['state'])
            self.outqueue.put(data['id'])
        elif(self.prepared_entity['parse'] == ParseType.NEW):
            dev = self.prepared_entity['data']['device']
            prop = self.prepared_entity['data']['property']
            prop_ref = KnowledgeGraph.add_property(
                prop['label'],
                prop['state'], 
                prop['last_updated'],
                prop['last_changed']
            )
            KnowledgeGraph.add_device(
                dev['label'],
                dev['actuator'],
                prop_ref, 
                dev['ha_name'],
                dev['ha_type']
            )
            self.outqueue.put(prop_ref)
        else:
            pass
    
    # Main method used to prepare the data of the parser
    def prepare(self):
        prepared_entity = {}
        self.ha_name = self.raw_entity['entity_id']
        self.ha_type = self.ha_name.split('.')[0]

        if (validEntity(self.ha_name)):
            self.device_ref = KnowledgeGraph.get_entity(pred=DOME.homeassistantname, obj=self.ha_name, isURI=False)

            if (self.device_ref is not None and len(self.device_ref) > 0):
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

    # Prepare the data for an update to the knowledge base
    def prepareUpdate(self):
        device_all = KnowledgeGraph.get_entity_by_id(str(self.device_ref[0]))
                
        # Get the device property
        prop_ref = None
        if (str(DOME.actuates) in device_all.keys()):
            prop_ref = device_all[str(DOME.actuates)]
        elif (str(DOME.observes) in device_all.keys()):
            prop_ref = device_all[str(DOME.observes)]
        
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
    
    # Prepare the data for a new addition to the knowledge base
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
                    'actuator': self.ha_type in config.ACTUATORS,
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