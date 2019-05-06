import sys
import os

import config

import websocket.ha_websocket as websocket
from parser.parser_2_0 import HALDParser
from kb import KnowledgeGraph
# import kb_init as kb_init

DOME = config.DOME_NAMESPACE

parser = HALDParser()

websocket.main()
f_num = parser.parse()

# g.serialize(destination=config.PATH_STORE, format='turtle', indent=2)