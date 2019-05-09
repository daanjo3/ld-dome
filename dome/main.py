import sys
import os

import dome.config as config

import dome.websocket.ha_websocket as websocket
from dome.parser.parser import HALDParser
from dome.util.kb import KnowledgeGraph

DOME = config.DOME_NAMESPACE

graph = KnowledgeGraph()

def show():
    print('--- Home ---')
    for home in graph.list_by_type(DOME.Home):
        print(home)
    print()
    
    print('--- Devices ---')
    for dev in graph.list_by_type(DOME.Device):
        print(dev)
    print()
    
    print('--- Properties ---')
    for prop in graph.list_by_type(DOME.Property):
        print(prop)
    print()

def reload_graph():
    graph.clear()
    parser = HALDParser(graph)
    websocket.main()
    f_num = parser.parse()
    print(str(f_num) + ' devices have been parsed')
    print(str(len(graph)) + ' triples are currently in the store')

if __name__ == "__main__":
    if(len(sys.argv) == 2 and sys.argv[1] == 'show'):
        show()
    elif(len(sys.argv) == 2 and sys.argv[1] == 'reload'):
        reload_graph()

        