from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json
# import sys
# import os

import dome.config as config

# import dome.websocket.ha_websocket as websocket
# from dome.parser.parser import HALDParser

from dome.util.kb import KnowledgeGraph

DOME = config.DOME_NAMESPACE
from rdflib import RDFS

graph = KnowledgeGraph()

def clearScreen():
    import subprocess, platform

    if platform.system()=="Windows":
        subprocess.Popen("cls", shell=True).communicate() #I like to use this instead of subprocess.call since for multi-word commands you can just type it out, granted this is just cls and subprocess.call should work fine 
    else: #Linux and Mac
        print("\033c", end="")

main_menu = [
    {
        'type': 'list',
        'name': 'main_menu',
        'message': 'Main Menu',
        'choices': ['Initialize', 'Configure', 'Status']
    }
]

def mainMenu():
    answers = prompt(main_menu)
    if(answers['main_menu'] == 'Initialize'):
        init()

init_menu_home = [
    {
        'type': 'input',
        'name': 'home',
        'message': 'Home name',
    }
]

init_menu_room = [
    {
        'type': 'input',
        'name': 'room',
        'message': 'Name a room'
    },
    {
        'type': 'confirm',
        'name': 'anotherOne',
        'message': 'Do you want to add another room?'
    }
]



def printPropertyList():
    dash = '-' * 158
    print(dash)
    print('{:<40} {:^40} {:>20}'.format('Label', 'actuatedBy | observedBy', 'Device'))
    print(dash)
    for prop in graph.get_entities_by_type(DOME.Property, mode=2):
        label = prop[str(RDFS.label)]
        device, action = None, None
        observedBy = graph.get_entity(pred=DOME.observes, obj=(prop['id']))
        if(observedBy):
            action = 'observed by'
            device = observedBy[0]
        actuatedBy = graph.get_entity(pred=DOME.actuates, obj=(prop['id']))
        if(actuatedBy):
            action = 'actuated by'
            device = actuatedBy[0]
        print('{:<40} {:^40} {:<20}'.format(label, action, device))

def printDeviceList():
    dash = '-' * 62
    print(dash)
    print('{:<20} {:^20} {:>20}'.format('Label', 'Actuates | Observes', 'Property'))
    print(dash)
    for dev in graph.get_entities_by_type(DOME.Device, mode=2):
        action = 'actuates'
        if (str(DOME.observes) in dev.keys()):
            action = 'observes'
        print('{:<20} {:^20} {:<20}'.format(str(dev[str(RDFS.label)]), action, graph.get_entity_by_id(dev['id'], mode=1)))

init_menu_device = [{
    'type': 'list',
    'name': 'devices',
    'message': 'Select a device to rename',
    'choices': []
    }
]

class CLIEntity():
    label = ""
    entity_id = ""

    def __init__(self, entity):
        self.label = entity[str(RDFS.label)]
        self.entity_id = entity['id']

    def __str__(self):
        return self.label

def init():
    clearScreen()
    home = prompt(init_menu_home)['home']

    clearScreen()
    rooms = []
    room_answer = prompt(init_menu_room)
    rooms.append(room_answer['room'])
    while(room_answer['anotherOne']):
        room_answer = prompt(init_menu_room)
        rooms.append(room_answer['room'])
    
    clearScreen()
    printDeviceList()
    init_menu_device[0]['choices'] = [{
        'name':dev[str(RDFS.label)],
        'value': dev['id']
        } for dev in graph.get_entities_by_type(DOME.Device, mode=2)]
    
    devices_answer = prompt(init_menu_device)
    print(devices_answer)

    # TODO To be Continued



if __name__ == "__main__":
    mainMenu()
    # printDeviceList()
    # printPropertyList()