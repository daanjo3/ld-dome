import os
from RDF import NS

# ------ PARSER ------ #

DEVICE_WHITELIST = ['device_tracker.48_60_5f_84_f3_e7', 'device_tracker.64_a2_f9_f5_de_ac', 'media_player.living_room_tv',
    'person.daan', 'person.janine', 'sensor.alarmtrigger', 'sensor.sonoff_status', 'sensor.sonoff_status_2', 'sun.sun', 'switch.sonoff', 'switch.sonoff_2',
]

DEVICE_BLACKLIST = ['sensor.yr_symbol']
ENTITY_WHITELIST = ['device_tracker', 'switch', 'sensor', 'media_player', 'light']

ACTUATORS = ['media_player', 'switch', 'light']

# ------ WEBSOCKET ------ #
ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI5NDE1ZjNiZTM1ODQ0NDc2YTNmZDg4OGYxY2M0NjNjMSIsImlhdCI6MTU1NTUzODIzOCwiZXhwIjoxODcwODk4MjM4fQ.CRMahk7jrvFbxcTa2Z1g1L2QzCUA4E257cd0zyFtGX8'

# ------ GRAPH - Namespaces------
DOME = NS('http://kadjanderman.com/ontology/')
DOME_DATA = NS('http://kadjanderman.com/resource/')
rdfs = NS('http://www.w3.org/2000/01/rdf-schema#')
rdf = NS('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

# ------ Benchmark ------- #
BM_LOG = 'benchmark01.csv'