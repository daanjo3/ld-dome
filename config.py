import os
from rdflib import Namespace

DEVICE_WHITELIST = ['device_tracker.48_60_5f_84_f3_e7', 'device_tracker.donkermobile', 'group.all_devices', 'group.all_switches', 'media_player.living_room_tv',
    'person.daan', 'person.janine', 'sensor.alarmtrigger', 'sensor.sonoff_status', 'sensor.sonoff_status_2', 'sun.sun', 'switch.sonoff', 'switch.sonoff_2', 'zone.home'
]

PATH = os.getcwd()

# --- WEBSOCKET ---
ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI5NDE1ZjNiZTM1ODQ0NDc2YTNmZDg4OGYxY2M0NjNjMSIsImlhdCI6MTU1NTUzODIzOCwiZXhwIjoxODcwODk4MjM4fQ.CRMahk7jrvFbxcTa2Z1g1L2QzCUA4E257cd0zyFtGX8'
WEBSOCKET_OUT_DEVICE = PATH + '/out/websocket/device/'
WEBSOCKET_OUT_CONFIG = PATH + '/out/websocket/config.json'
WEBSOCKET_OUT_SERVICE = PATH + '/out/websocket/services.json'

# --- PARSER ---
PARSER_IN_DEVICE = WEBSOCKET_OUT_DEVICE
PARSER_OUT_DEVICE = PATH + '/out/parser/'

# --- TRIPLE STORE ---
DOME_NAMESPACE = Namespace('http://kadjanderman.com/ontology/')
PATH_STORE = PATH + '/store.nt'

# --- KNOWLEDGE BASE ---
KB_PATH = PATH + '/out/knowledgebase/'

KB_DEVICE = KB_PATH + 'device/'
KB_FOI = KB_PATH + 'featureofinterest/'
KB_HOME = KB_PATH + 'home/'
KB_PROPERTY = KB_PATH + 'property/'
KB_ROOM = KB_PATH + 'room/'