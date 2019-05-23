# Parser which is directly called from the websocket output

import json
import os
import copy

from rdflib.namespace import RDF, RDFS
from rdflib import Literal

import dome.config as config
from dome.util.kb import KnowledgeGraph

DOME = config.DOME_NAMESPACE
DOME_DATA = config.DOME_DATA_NAMESPACE

graph = KnowledgeGraph()

# Parse a single device and create a new device entity
def parseDevice(device):
    label = None
    ha_name = str(device['entity_id'])
    ha_type = ha_name.split('.')[0]
    actuator = ha_type in ['media_player', 'switch']

    try:
        label = device['attributes']['friendly_name']
    except KeyError:
        label = device['entity_id']
    
    prop_ref = parseProperty(device)

    graph.add_device(label, actuator, prop_ref, ha_name, ha_type)

# Parse a single property and create a new property entity
def parseProperty(device):
    prop_ref = graph.add_property(
        device['entity_id'],
        device['state'],
        device['last_updated'],
        device['last_changed']
    )
    return prop_ref


def updateProperty(kb_entity, state):
    kb_dev = graph.get_entity_by_id(str(kb_entity))
    kb_prop = None
    if (str(DOME.actuates) in kb_dev.keys()):
        kb_prop = graph.get_entity_by_id(kb_dev[str(DOME.actuates)])
    elif (str(DOME.observes) in kb_dev.keys()):
        kb_prop = graph.get_entity_by_id(kb_dev[str(DOME.observes)])
    else:
        print("Cannot update updateProperty")

    graph.modify_literal(kb_prop['id'], DOME.last_changed, state['last_changed'])
    graph.modify_literal(kb_prop['id'], DOME.last_updated, state['last_updated'])
    graph.modify_literal(kb_prop['id'], DOME.value, state['state'])

def parseEntityDump(ha_entities):
    for entity in ha_entities:
        print(entity['entity_id'])
        ha_name = entity['entity_id']
        ha_type = ha_name.split('.')[0]

        if (ha_type in config.ENTITY_WHITELIST and ha_name != 'sensor.yr_symbol'):
            kb_entity = graph.get_entity(pred=DOME.homeassistantname, obj=ha_name, isURI=False)
            if (len(kb_entity) == 0): kb_entity = None
            if (kb_entity is not None):
                updateProperty(kb_entity[0], entity)
            else:
                parseDevice(entity)

def parseEvent(event):
    ha_name = event['entity_id']
    kb_entity = graph.get_entity(pred=DOME.homeassistantname, obj=ha_name, isURI=False)

    if (len(kb_entity) == 0): kb_entity = None

    if (kb_entity is not None):
        updateProperty(kb_entity[0], event['new_state'])
    else:
        print(ha_name)
        print("Cannot update entity")
        print("Please update device list")
        # TODO figure out where to do the following:
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(loadEntities())
        # loop.close()