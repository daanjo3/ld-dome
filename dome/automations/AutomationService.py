from multiprocessing import Process

from dome.util.KnowledgeGraph import KnowledgeGraph
from dome.lib.observable import Observable
from dome.automations.AutomationResolver import Resolver
from dome.config import DOME_NAMESPACE as DOME

class AutomationService(Process, Observable):
    pool = []
    kb_readable = None
    watchlist = []

    def __init__(self, queue, kb_readable):
        Process.__init__(self)
        Observable.__init__(self)
        self.queue = queue
        self.kb_readable = kb_readable
        # self.loadAutomations()
    
    def register(self, callback):
        super(AutomationService, self).register(callback)
        for r in self.pool:
            r.register(callback)
    
    def registerNode(self, resolver):
        if (len(self.callbacks) > 0):
            for callback in self.callbacks:
                resolver.register(callback)         
    
    def run(self):
        self.notify('[{}] Starting service'.format(self.name))
        self.loadAutomations()
        try:
            while(True):
                prop_ref = self.queue.get(block=True)
                self.notify('[{}] Property Update received'.format(self.name))
                automation_relevant = self.wakeAutomationList(prop_ref)
                if (automation_relevant):
                    self.notify('[{}] Spawning Automations'.format(self.name))
                    for automation in automation_relevant:
                        r = Resolver(self.kb_readable, automation)
                        self.registerNode(r)
                        self.pool.append(r)
                        r.start()
        
        except KeyboardInterrupt:
            for r in self.pool:
                r.join()

    # TODO Update to enable nested triggers
    def loadAutomations(self):
        self.kb_readable.wait()
        automations = KnowledgeGraph.get_entities_by_type(DOME.Automation, mode=2)
        self.notify('[{}] Loading Automations: {}'.format(self.name, len(automations)))
        # self.notify('[{}] Automations:\n{}'.format(self.name, automations))

        for automation in automations:
            trigger = KnowledgeGraph.get_entity_by_id(automation[str(DOME.triggeredby)])
            trigger_conditions = KnowledgeGraph.cleanPropertyList(trigger, str(DOME.hascondition))

            for condition_id in trigger_conditions:
                condition = KnowledgeGraph.get_entity_by_id(condition_id)
                prop = KnowledgeGraph.get_entity_by_id(condition[str(DOME.observes)])

                self.watchlist.append({
                    'prop_ref': str(prop['id']),
                    'enabled': bool(automation[str(DOME.enabled)]),
                    'automation_id': str(automation['id'])
                })
        self.notify('[{}] Automation loading done.'.format(self.name))
    
    def wakeAutomationList(self, prop_ref):
        automation_list = []
        for watch in self.watchlist:
            if (watch['prop_ref'] == prop_ref and watch['enabled']):
                automation_list.append(watch['automation_id'])
        return list(set(automation_list))
