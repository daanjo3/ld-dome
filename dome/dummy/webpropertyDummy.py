from dome.db.graph import Graph
from dome.config import DOME, rdf

def loadWebProperty():
    webproperties = Graph.getModel().get_sources(rdf.type, DOME.WebProperty)
    wp_len = 0
    for wp in webproperties:
        print('got wp')
        wp_len += 1
    print(wp_len)
    if (wp_len > 0):
        return False
    
    print('[TEST] Creating WebProperty')

    label = 'Princenhage Precipitation'
    host = 'http://localhost:8890/sparql'
    graph = 'urn:graph:dummy:princenhage'
    resource_ref = 'http://example.org/princenhageweather'
    property_ref = 'http://example.org/ns#precipitation'
    poll = 1

    Graph.addWebProperty(label, host, resource_ref, property_ref, poll, graph=graph)