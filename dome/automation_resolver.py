from dome.util.kb import KnowledgeGraph
# from dome.websocket.socket_update import HAStateListener

graph = KnowledgeGraph()

def test_create_condition(graph):
    print('Creating condition')

    label = 'is het bedlampje aan?'
    observes = 'http://kadjanderman.com/resource/property/80190dc8-91dc-4416-88bf-aba4669b191c'
    tState = 'on'
    return graph.add_condition(label, observes, tState)

def test_create_trigger(graph):
    print('Creating trigger')

    cond = test_create_condition()
    return graph.add_trigger(cond)

def test_create_action(graph):
    print('Creating action')

    label = 'zet de kamerlamp aan.'
    command = 'turn_on'
    actuates = 'http://kadjanderman.com/resource/property/70f176fe-d191-467c-921c-5cc5107ffdb8'
    return graph.add_action(label, command, actuates)

def test_create_automation(graph):
    print('Creating automation')

    label = 'testAutomation'
    trigger = test_create_trigger()
    action = test_create_action()

    automation = graph.add_automation(label, trigger, action)

if __name__ == "__main__":
    test_create_automation()