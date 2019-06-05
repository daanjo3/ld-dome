from dome.util.KnowledgeGraph import KnowledgeGraph
from dome.config import DOME_NAMESPACE as DOME

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

def loadDummyAutomations():
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