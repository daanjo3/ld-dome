from multiprocessing import Manager, Process, Queue, Lock, Event
from dome.lib.observable import Observable
from dome.lib.state import BaseState
from dome.parser.HAParser import HAParser
from dome.parser.WParser import WParser

class Origin:
    HA_LOADER = 'HALoader'
    HA_UPDATER = 'HAUpdater'
    WEB_UPDATER = 'WebUpdater'

class State(BaseState):
    WAITING_QUEUE = (1, 'WAITING READ VALIDATE')
    PROCESSING = (2, 'PROCESSING PAYLOAD')
    SPAWN = (3, 'SPAWNING WORKER')
    TERMINATE = (4, 'TERMINATING WORKERS')

# Thread manager that spawns a worker for each parse updated entity
class ParserService(Process, Observable):
    state = State()
    pool = []
    kb_lock = Lock()
    
    def __init__(self, dome):
        Process.__init__(self)
        Observable.__init__(self)
        self.dome = dome
        self.inqueue = dome.parser_queue
        # self.outqueue = dome.automation_queue
        # self.kb_event = dome.graph_readable_event
    
    def register(self, callback):
        super(ParserService, self).register(callback)
        for p in self.pool:
            p.register(callback)
    
    def registerNode(self, parser):
        if (len(self.callbacks) > 0):
            for callback in self.callbacks:
                parser.register(callback)

    def spawnHAP(self, payload):
        p = HAParser(self.dome, payload, self.kb_lock)
        self.registerNode(p)
        self.pool.append(p)
        p.start()
    
    def spawnWP(self, payload):
        p = WParser(self.dome, payload, self.kb_lock)
        self.registerNode(p)
        self.pool.append(p)
        p.start()
    
    def run(self):
        try:
            while(True):
                self.update(State.WAITING_QUEUE)
                origin, payload = self.inqueue.get(block=True)
                self.update(State.PROCESSING, origin=origin)

                if (origin == Origin.HA_LOADER):
                    # If the origin is the loader split the data in multiple parts
                    for part in payload:
                        self.update(State.SPAWN)
                        self.spawnHAP(part)
                
                elif (origin == Origin.HA_UPDATER):
                    # If the origin is the updater spawn a single worker
                    self.update(State.SPAWN)
                    self.spawnHAP(payload)
                
                elif (origin == Origin.WEB_UPDATER):
                    self.update(State.SPAWN)
                    self.spawnWP(payload)
                else:
                    pass
        except KeyboardInterrupt:
            self.update(State.TERMINATE)
            for p in self.pool:
                p.join()
        self.update(State.FINISHED)
    
    def update(self, state, origin=None):
        self.state.update(state)
        msg = '[{}] {}'.format(self.name, self.state)
        if (origin):
            msg += ' FROM {}'.format(origin)
        self.notify(msg)