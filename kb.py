import os
import json

import config
import parser.ld_templates as templates

def list_homes():
    print(os.listdir(config.KB_HOME))

def list_rooms():
    print(os.listdir(config.KB_ROOM))

def list_devices():
    print(os.listdir(config.KB_DEVICE))

def list_properties():
    print(os.listdir(config.KB_PROPERTY))

def list_foi():
    print(os.listdir(config.KB_FOI))

def add_home(label):
    home = copy.copy(templates.TEMPLATE_HOME)
    home['@id'] = 'home_' + label
    home['label'] = label
    with open(config.KB_HOME + home['@id'], 'w') as f:
        json.dump(home, f, indent=2)
    return home

def add_room(label, home):
    room = copy.copy(templates.TEMPLATE_ROOM)
    room['@id'] = 'room_' + label
    room['label'] = label
    room['partOf'] = home
    with open(config.KB_ROOM + room['@id'], 'w') as f:
        json.dump(room, f, indent=2)
    return room

def add_foi(label, room, properties):
    foi = copy.copy(templates.TEMPLATE_FOI)
    foi['@id'] = 'foi_' + label
    foi['label'] = label
    foi['featureOfInterestOf'] = room
    foi['hasProperty'] = properties
    with open(config.KB_FOI + foi['@id'], 'w') as f:
        json.dump(foi, f, indent=2)
    return foi
    