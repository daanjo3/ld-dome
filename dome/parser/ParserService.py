from multiprocessing import Manager, Process, Queue, Lock, Event
from dome.lib.observable import Observable
from dome.parser.HAParser import Parser

# Thread manager that spawns a worker for each parse updated entity
class ParserService(Process, Observable):
    pool = []
    kb_lock = Lock()
    
    def __init__(self, inqueue, outqueue, kb_readable):
        Process.__init__(self)
        Observable.__init__(self)
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.kb_event = kb_readable
    
    def register(self, callback):
        super(ParserService, self).register(callback)
        for p in self.pool:
            p.register(callback)
    
    def registerNode(self, parser):
        if (len(self.callbacks) > 0):
            for callback in self.callbacks:
                parser.register(callback)

    def spawn(self, payload):
        p = Parser(payload, self.kb_event, self.kb_lock, self.outqueue)
        self.registerNode(p)
        self.pool.append(p)
        p.start()
    
    def run(self):
        try:
            while(True):
                origin, payload = self.inqueue.get(block=True)
                self.notify('[{}] Payload from {}'.format(self.name, origin))

                if (origin == ParserService.Origin.HA_LOADER):
                    # If the origin is the loader split the data in multiple parts
                    for part in payload:
                        self.spawn(part)
                
                elif (origin == ParserService.Origin.HA_UPDATER):
                    # If the origin is the updater spawn a single worker
                    self.spawn(payload)
                
                else:
                    pass
        except KeyboardInterrupt:
            for p in self.pool:
                p.join()
    
    class Origin:
        HA_LOADER = 'HALoader'
        HA_UPDATER = 'HAUpdater'