from dome.util.KnowledgeGraph import KnowledgeGraph
from dome.config import DOME

def loadWebProperty():
    webproperties = KnowledgeGraph.get_entities_by_type(DOME.WebProperty)
    if (len(webproperties) > 0):
        print('[TEST] No WebProperty created, already present')
        return False
    
    print('[TEST] Creating WebProperty')

    label = 'Princenhage Precipitation'
    host = 'http://localhost:8890/sparql'
    graph = 'urn:graph:dummy:princenhage'
    resource_ref = 'http://example.org/princenhageweather'
    property_ref = 'http://example.org/ns#precipitation'
    poll = 1

    KnowledgeGraph.add_webproperty(label, host, resource_ref, property_ref, poll, graph=graph)