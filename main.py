import sys
import os
import json

from rdflib import Graph, plugin, RDF, URIRef, Namespace
from rdflib.serializer import Serializer

import config

import websocket.ha_websocket as websocket
from parser.parser import HALDParser
# import kb_init as kb_init

DOME = Namespace('http://kadjanderman.com/ontology/')
print(DOME.value)


# g = Graph()
# parser = HALDParser(g)

# websocket.main()
# parser.parse()

# device_list = []
# for fp in os.listdir(config.KB_DEVICE):
#     with open(config.KB_DEVICE + fp, 'rb') as f:
#         g.parse(data=f.read(), format='json-ld')
# for fp in os.listdir(config.KB_PROPERTY):
#     with open(config.KB_PROPERTY + fp, 'rb') as f:
#         g.parse(data=f.read(), format='json-ld')

# print(g.serialize())

# type_property = URIRef("http://www.kadjanderman.com/ontology/class/Device")
# for s, p, o in g.triples( (None, RDF.type, type_property) ):
#     print('s: '+s)
#     print()

# g.serialize(destination='./test.json', format='json-ld', indent=2)