import sys
import os

import dome.config as config

import dome.websocket.ha_websocket as websocket
from dome.parser.parser import HALDParser
from dome.util.kb import KnowledgeGraph

DOME = config.DOME_NAMESPACE
from rdflib import RDFS

graph = KnowledgeGraph()

def show():
    print('--- Home ---')
    for home in graph.get_entities_by_type(DOME.Home):
        print(home)
    print()
    
    print('--- Devices ---')
    for dev in graph.get_entities_by_type(DOME.Device):
        print(dev)
    print()
    
    print('--- Properties ---')
    for prop in graph.get_entities_by_type(DOME.Property):
        print(prop)
    print()

def reload_graph():
    graph.purge()
    parser = HALDParser(graph)
    websocket.main()
    f_num = parser.parse()
    print(str(f_num) + ' devices have been parsed')
    print(str(len(graph)) + ' triples are currently in the store')

class TestPrint():
    def modify_literal_m():
        print(graph.modify_literal_m())

if __name__ == "__main__":
    if(len(sys.argv) == 2 and sys.argv[1] == 'show'):
        show()
    elif(len(sys.argv) == 2 and sys.argv[1] == 'reload'):
        reload_graph()
    elif(len(sys.argv) == 3 and sys.argv[1] == 'test'):
        if (sys.argv[2] == 'entity'):
            test_entity()
        if (sys.argv[2] == 'modify'):
            TestPrint().modify_literal_m()

        