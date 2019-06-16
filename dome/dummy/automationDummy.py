from dome.util.KnowledgeGraph import KnowledgeGraph
from dome.config import DOME_NAMESPACE as DOME

def test_create_condition():
    label = 'is het bedlampje aan?'
    observes = 'http://kadjanderman.com/resource/property/3f5faa35-134c-4b2a-8f6a-d6fa4c485c52'
    tState = 'on'
    return KnowledgeGraph.add_condition(label, observes, tState)

def test_create_trigger():
    cond = test_create_condition()
    return KnowledgeGraph.add_trigger(cond)

def test_create_action():
    label = 'zet de kamerlamp aan.'
    command = 'turn_on'
    actuates = 'http://kadjanderman.com/resource/property/211491e6-f2c4-4c94-b628-f55397983a23'
    return KnowledgeGraph.add_action(label, actuates, command)

def loadAutomation():
    automations = KnowledgeGraph.get_entities_by_type(DOME.Automation)
    if (len(automations) > 0):
        print('[TEST] No Automation created, already present')
        return False
    
    # Automation
    label = 'testAutomation'
    trigger = test_create_trigger()
    action = [test_create_action()]
    automation = KnowledgeGraph.add_automation(label, trigger, action)
    return True