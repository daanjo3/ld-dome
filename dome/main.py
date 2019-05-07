import sys
import os

import dome.config as config

import dome.websocket.ha_websocket as websocket
from dome.parser.parser import HALDParser
from dome.util.kb import KnowledgeGraph

DOME = config.DOME_NAMESPACE

parser = HALDParser()

websocket.main()
f_num = parser.parse()

print(f_num)

# g.serialize(destination=config.PATH_STORE, format='turtle', indent=2)