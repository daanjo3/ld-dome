from multiprocessing import Process

from dome.lib.observable import Observable
from dome.lib.state import BaseState

# from dome.util.KnowledgeGraph import KnowledgeGraph
from dome.db.graph import Graph
from dome.automations.AutomationResolver import Resolver

# from dome.config import DOME_NAMESPACE as DOME
from RDF import NS
DOME = NS('http://kadjanderman.com/ontology/')
DOME_DATA = NS('http://kadjanderman.com/resource/')
# These current do not generate valid URIs
rdf = NS('https://www.w3.org/TR/rdf-schema/')
rdfs = rdf

class State(BaseState):
    WAITING_READ_LOAD = (1, 'WAITING READ LOAD')
    LOAD = (2, 'LOADING AUTOMATIONS')
    WAITING_QUEUE = (3, 'WAITING FOR QUEUE')
    PROCESSING = (4, 'PROCESSING UPDATE')
    SPAWN = (5, 'SPAWNING WORKER')
    TERMINATE = (7, 'TERMINATING WORKERS')

class AutomationService(Process, Observable):    
    state = State()
    pool = []
    kb_readable = None
    watchlist = []

    def __init__(self, dome):
        Process.__init__(self)
        Observable.__init__(self)
        self.queue = dome.automation_queue
        self.kb_readable = dome.graph_readable_event
        self.dome = dome
    
    def register(self, callback):
        super(AutomationService, self).register(callback)
        for r in self.pool:
            r.register(callback)
    
    def registerNode(self, resolver):
        if (len(self.callbacks) > 0):
            for callback in self.callbacks:
                resolver.register(callback)         
    
    def run(self):
        self.update(State.WAITING_READ_LOAD)
        self.kb_readable.wait()
        self.update(State.LOAD)
        self.loadAutomations()
        try:
            while(True):
                self.update(State.WAITING_QUEUE)
                prop_ref = self.queue.get(block=True)
                self.update(State.PROCESSING)
                automation_relevant = self.wakeAutomationList(prop_ref)
                if (automation_relevant):
                    for automation in automation_relevant:
                        self.update(State.SPAWN)
                        r = Resolver(self.dome, automation)
                        self.registerNode(r)
                        self.pool.append(r)
                        r.start()
        
        except KeyboardInterrupt:
            self.update(State.TERMINATE)
            for r in self.pool:
                r.join()
        self.update(State.FINISHED)

    # TODO Update for REDLAND
    # TODO Update to enable nested triggers
    def loadAutomations(self):
        automations = KnowledgeGraph.get_entities_by_type(DOME.Automation, mode=2)
        automations = Graph.getModel().get_sources(rdf.type, DOME.Automation)

        for automation in automations:
            trigger = Graph.get_target(automation, DOME.triggeredby)
            # trigger = KnowledgeGraph.get_entity_by_id(automation[str(DOME.triggeredby)])
            trigger_conditions = KnowledgeGraph.cleanPropertyList(trigger, str(DOME.hascondition))

            for condition_id in trigger_conditions:
                condition = KnowledgeGraph.get_entity_by_id(condition_id)
                prop = KnowledgeGraph.get_entity_by_id(condition[str(DOME.observes)])

                self.watchlist.append({
                    'prop_ref': str(prop['id']),
                    'enabled': bool(automation[str(DOME.enabled)]),
                    'automation_id': str(automation['id'])
                })
    
    def wakeAutomationList(self, prop_ref):
        automation_list = []
        for watch in self.watchlist:
            if (watch['prop_ref'] == prop_ref and watch['enabled']):
                automation_list.append(watch['automation_id'])
        return list(set(automation_list))
    
    def update(self, state):
        self.state.update(state)
        self.notify('[{}] {}'.format(self.name, self.state))
