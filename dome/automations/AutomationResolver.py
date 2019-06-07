from multiprocessing import Process
import asyncio

from dome.util.KnowledgeGraph import KnowledgeGraph
from dome.lib.observable import Observable
from dome.lib.state import BaseState
from dome.websocket.HAService import call

from dome.config import DOME_NAMESPACE as DOME
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

    def __init__(self, kb_readable, automation_id):
        Process.__init__(self)
        Observable.__init__(self)
        self.kb_readable = kb_readable
        self.automation_id = automation_id
    
    def run(self):
        # Wait until the kb is readable and validate the trigger
        self.update(State.WAITING_READ_VALIDATE)
        self.kb_readable.wait()
        self.update(State.VALIDATING)
        valid = self.validate()
        if (not valid):
            self.update(State.ABORTED)
            return
        
        # Wait until the kb is readable again and prepare
        self.update(State.WAITING_READ_PREPARE)
        self.kb_readable.wait()
        self.update(State.PREPARE)
        actions = self.prepare()

        # Call the HA service through the websocket
        self.update(State.SERVICE_CALL)
        loop = asyncio.get_event_loop()
        tasks = []
        for action in actions:
            tasks.append(asyncio.ensure_future(call(action['domain'], action['service'], action['entity_id'])))
        loop.run_until_complete(asyncio.gather(*tasks))

        self.update(State.FINISHED)
    
    
    # TODO extend for nested triggers
    # Validate the trigger
    def validate(self):
        self.automation = KnowledgeGraph.get_entity_by_id(self.automation_id)
        trigger = KnowledgeGraph.get_entity_by_id(self.automation[str(DOME.triggeredby)])
        trigger_conditions = KnowledgeGraph.cleanPropertyList(trigger, str(DOME.hascondition))

        valid = True
        for condition_id in trigger_conditions:
            condition = KnowledgeGraph.get_entity_by_id(condition_id)
            valid = valid and self.verify(condition)
        return valid
    
    # Gather all service calls from the KB
    def prepare(self):
        actions_ids = KnowledgeGraph.cleanPropertyList(self.automation, str(DOME.performsaction))
        actions = []
        for action_id in actions_ids:
            # Load action resource
            action = KnowledgeGraph.get_entity_by_id(action_id)
            # Obtain prop_id, with it's relevant device
            prop_id = action[str(DOME.actuates)]
            actuator_ids = KnowledgeGraph.get_entity(pred=DOME.actuates, obj=prop_id) + KnowledgeGraph.get_entity(pred=DOME.observes, obj=prop_id)
            dev_id = [act_id for act_id in actuator_ids if 'device' in act_id][0]
            device = KnowledgeGraph.get_entity_by_id(dev_id)

            actions.append({
                'domain': device[str(DOME.homeassistanttype)],
                'service': action[str(DOME.command)],
                'entity_id': device[str(DOME.homeassistantname)]
            })
        return actions
    
    # Verify one specific condition
    def verify(self, condition):
        prop = KnowledgeGraph.get_entity_by_id(condition[str(DOME.observes)])

        target_state = condition[str(DOME.targetState)]
        prop_state = prop[str(DOME.value)]

        if (target_state == prop_state):
            return True
        return False
    
    def update(self, state):
        self.state.update(state)
        self.notify('[{}] {}'.format(self.name, self.state))