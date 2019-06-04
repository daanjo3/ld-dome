import asyncio

from rdflib.namespace import RDFS

from dome.util.kb import KnowledgeGraph
from dome.lib.observable import Observable
from dome.config import DOME_NAMESPACE as DOME
import dome.websocket.socket_service as service
# from dome.websocket.socket_update import HAStateListener

def getTriggerConditions(trigger):
    trigger_conditions = trigger[str(DOME.hascondition)]
        # Loop over the conditions in the trigger
    if (not isinstance(trigger_conditions, list)):
        trigger_conditions = [trigger_conditions]
    return trigger_conditions

def getAutomationActions(automation):
    automation_actions = automation[str(DOME.performsaction)]

    if (not isinstance(automation_actions, list)):
        automation_actions = [automation_actions]
    return automation_actions

def getHaAlias(action):
    prop_id = action[str(DOME.actuates)]
    actuator_ids = KnowledgeGraph.get_entity(pred=DOME.actuates, obj=prop_id) + KnowledgeGraph.get_entity(pred=DOME.observes, obj=prop_id)
    dev_id = [act_id for act_id in actuator_ids if 'device' in act_id][0]
    device = KnowledgeGraph.get_entity_by_id(dev_id)

    domain = device[str(DOME.homeassistanttype)]
    entity_id = device[str(DOME.homeassistantname)]
    return domain, entity_id

def generateServiceCalls(automation):
    action_ids = getAutomationActions(automation)
    actions = []
    for action_id in action_ids:
        action = KnowledgeGraph.get_entity_by_id(action_id)

        service = action[str(DOME.command)]
        domain, entity_id = getHaAlias(action)
        actions.append({
            'domain': domain,
            'service': service,
            'entity_id': entity_id
        })
    return actions
    
        

def singleton(cls):
    return cls()

@singleton
class AutomationResolver(Observable):
    watchlist = []

    def add(self, automation):
        trigger = KnowledgeGraph.get_entity_by_id(automation[str(DOME.triggeredby)])
        trigger_conditions = getTriggerConditions(trigger)
        for c in trigger_conditions:
            condition = KnowledgeGraph.get_entity_by_id(c)
            prop = KnowledgeGraph.get_entity_by_id(condition[str(DOME.observes)])
            self.watchlist.append({
                'prop_id': str(prop['id']),
                'automation_id': str(automation['id'])
            })
    
    def verify(self, condition):
        prop = KnowledgeGraph.get_entity_by_id(condition[str(DOME.observes)])

        target_state = condition[str(DOME.targetState)]
        prop_state = prop[str(DOME.value)]

        if (target_state == prop_state):
            return True
        return False
        
    def resolve(self, automation_id):
        print('[RESOLVER] Trying to resolve automation')
        automation = KnowledgeGraph.get_entity_by_id(automation_id)
        isEnabled = bool(automation[str(DOME.enabled)])
        trigger = KnowledgeGraph.get_entity_by_id(automation[str(DOME.triggeredby)])
        trigger_conditions = getTriggerConditions(trigger)
        # Loop over the conditions in the trigger
        valid = True
        for c in trigger_conditions:
            condition = KnowledgeGraph.get_entity_by_id(c)
            valid = valid and self.verify(condition)
        
        if(valid):
            self.notify(generateServiceCalls(automation))
        else:
            print('[RESOLVER] Automation is NOT triggered')

    def onUpdate(self, prop_id):
        prop = KnowledgeGraph.get_entity_by_id(prop_id)
        for entry in self.watchlist:
            if prop_id == entry['prop_id']:
                self.resolve(entry['automation_id'])

def test_create_condition():
    print('[TEST] Creating condition')

    label = 'is het bedlampje aan?'
    observes = 'http://kadjanderman.com/resource/property/9912b71b-a83e-49b6-bccb-5f59ccdab490'
    tState = 'on'
    return KnowledgeGraph.add_condition(label, observes, tState)

def test_create_trigger():
    print('[TEST] Creating trigger')

    cond = test_create_condition()
    return KnowledgeGraph.add_trigger(cond)

def test_create_action():
    print('[TEST] Creating action')

    label = 'zet de kamerlamp aan.'
    command = 'turn_on'
    actuates = 'http://kadjanderman.com/resource/property/665f7fbb-d6b4-443a-bceb-e6dc63cd6f8e'
    return KnowledgeGraph.add_action(label, actuates, command)

def test_create_automation():
    automations = KnowledgeGraph.get_entities_by_type(DOME.Automation)
    if (len(automations) > 0):
        print('[TEST] No automation created, already present')
        return False
    
    print('[TEST] Creating automation')
    
    label = 'testAutomation'
    trigger = test_create_trigger()
    action = [test_create_action()]

    automation = KnowledgeGraph.add_automation(label, trigger, action)
    return True

if __name__ == "__main__":
    test_create_automation()