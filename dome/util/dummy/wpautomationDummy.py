from dome.util.KnowledgeGraph import KnowledgeGraph
from dome.config import DOME_NAMESPACE as DOME

def test_create_condition():
    label = 'Regent het?'
    observes = 'http://kadjanderman.com/resource/property/web/26f41707-967f-4410-a1f9-a0afe163450d'
    tState = '69'
    return KnowledgeGraph.add_condition(label, observes, tState)

def test_create_trigger():
    cond = test_create_condition()
    return KnowledgeGraph.add_trigger(cond)

def test_create_action():
    label = 'zet de kamerlamp aan.'
    command = 'turn_on'
    actuates = 'http://kadjanderman.com/resource/property/211491e6-f2c4-4c94-b628-f55397983a23'
    return KnowledgeGraph.add_action(label, actuates, command)

def loadWPAutomation():
    automations = KnowledgeGraph.get_entities_by_type(DOME.Automation)
    if (len(automations) > 1):
        print('[TEST] No Automation created, already present')
        return False
    
    # Automation
    label = 'WPTestAutomation'
    trigger = test_create_trigger()
    action = [test_create_action()]
    automation = KnowledgeGraph.add_automation(label, trigger, action)
    return True
