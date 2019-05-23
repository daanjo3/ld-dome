import sys
import os
import re
import copy

import dome.config as config

import dome.websocket.ha_websocket as websocket
from dome.parser.parser import HALDParser
from dome.util.kb import KnowledgeGraph

DOME = config.DOME_NAMESPACE
from rdflib import RDFS

graph = KnowledgeGraph()

def show():
    print('-------- Locations --------')
    locations = zip(graph.get_entities_by_type(DOME.Home) + graph.get_entities_by_type(DOME.Room),
        graph.get_entities_by_type(DOME.Home, mode=1) + graph.get_entities_by_type(DOME.Room, mode=1))
    for loc_id, loc_label in locations:
        print("id: {}\nlabel: {}\n".format(loc_id, loc_label))
    print('--------------------------\n')
    
    print('--------- Devices ----------')
    devices = zip(graph.get_entities_by_type(DOME.Device), graph.get_entities_by_type(DOME.Device, mode=1))
    for dev_id, dev_label in devices:
        print("id: {}\nlabel: {}\n".format(dev_id, dev_label))
    print('--------------------------\n')
    
    print('-------- Properties --------')
    properties = zip(graph.get_entities_by_type(DOME.Property), graph.get_entities_by_type(DOME.Property, mode=1))
    for prop_id, prop_label in properties:
        print("id: {}\nlabel: {}\n".format(prop_id, prop_label))
    print('--------------------------\n')

    print('--- Features Of Interest ---')
    features = zip(graph.get_entities_by_type(DOME.FeatureOfInterest), graph.get_entities_by_type(DOME.FeatureOfInterest, mode=1))
    for foi_id, foi_label in features:
        print("id: {}\nlabel: {}\n".format(foi_id, foi_label))
    print('--------------------------\n')

def reload_graph():
    graph.purge()
    parser = HALDParser(graph)
    websocket.main()
    f_num = parser.parse()
    print(str(f_num) + ' devices have been parsed')
    print(str(len(graph)) + ' triples are currently in the store')

def rename_properties():
    for prop in graph.get_entities_by_type(DOME.Property, mode=2):
        label = prop[str(RDFS.label)]
        old_label = copy.copy(label)
        match_sensor_sonoff = label.split('_')[0] == 'sensor.sonoff' and label.split('.')[-1] != "connectivity"
        match_switch_sonoff = label.split('_')[0] == 'switch.sonoff' and label.split('.')[-1] != "state"
        match_media_player = label.split('.')[0] == 'media_player' and label.split('.')[-1] != "state"
        match_device_tracker = label.split('.')[0] == 'device_tracker' and label.split('.')[-1] != "presence"

        if (match_sensor_sonoff):
            label += '.connectivity'
        if (match_switch_sonoff or match_media_player):
            label += '.state'
        if (match_device_tracker):
            label += '.presence'
        
        
        if (old_label == label):
            print("No Properties renamed: already named properly\n")
            return
        else:
            print("Renaming Property: {} to {}".format(old_label, label))
        graph.modify_literal(prop['id'], RDFS.label, label)
    print("")

def create_locations():
    home = None
    if (not graph.get_entities_by_type(DOME.Home) and not graph.get_entities_by_type(DOME.Room)):
        # Adding home
        print("Creating Home: MatchBox")
        home = graph.add_home("MatchBox")

        # Adding Rooms
        print("Creating Room: Bedroom")
        graph.add_room("Bedroom", str(home))

        print("Creating Room: Living Room")
        graph.add_room("Living Room", str(home))
    else:
        print("No Locations added: already present")

    print("")

def create_fois():
    if (not graph.get_entities_by_type(DOME.FeatureOfInterest)):

        # Create Kamerlamp
        living_room_id = str(graph.get_entity(pred=RDFS.label, obj="Living Room", isURI=False)[0])
        kamerlamp_sensor = str(graph.get_entity(pred=RDFS.label, obj="sensor.sonoff_status_2.connectivity", isURI=False)[0])
        kamerlamp_actuator = str(graph.get_entity(pred=RDFS.label, obj="switch.sonoff_2.state", isURI=False)[0])

        print("Creating Feature of Interest: Kamerlamp")
        graph.add_foi("Kamerlamp", living_room_id, [kamerlamp_sensor, kamerlamp_actuator])

        # Create Nachtlamp
        bedroom_id = str(graph.get_entity(pred=RDFS.label, obj="Bedroom", isURI=False)[0])
        nachtlamp_sensor = str(graph.get_entity(pred=RDFS.label, obj="sensor.sonoff_status.connectivity", isURI=False)[0])
        nachtlamp_actuator = str(graph.get_entity(pred=RDFS.label, obj="switch.sonoff.state", isURI=False)[0])

        print("Creating Feature of Interest: Nachtlamp")
        graph.add_foi("Nachtlamp", bedroom_id, [nachtlamp_sensor, nachtlamp_actuator])
    else:
        print("No Features of Interest added: already present")

    print("")

def create_testroutine():
    pass

if __name__ == "__main__":
    if(len(sys.argv) == 2 and sys.argv[1] == 'show'):
        show()
    elif(len(sys.argv) == 3 and sys.argv[1] == 'phase'):
        if (sys.argv[2] == '0' or sys.argv[2] == 'all'):
            print('--- Loading a new graph from Home Assistant ---')
            reload_graph()
        if (sys.argv[2] == '1' or sys.argv[2] == 'all'):
            print('--- Renaming Properties ---')
            rename_properties()
            print('--- Creating Locations ---')
            create_locations()
            print("--- Creating Features of Interest ---")
            create_fois()
        if (sys.argv[2] == '2' or sys.argv[2] == 'all'):
            create_testroutine()
        

        