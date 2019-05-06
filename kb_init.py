"""
Main - main.py
This program creates a first batch of data for the knowledge base of the system.

The program contains steps which incrementally creates and enriches linked data objects
in the form of JSON-LD.

-- Create the Home entity and Room entities -- 
First a Home object is created, which represents both the physical and logical home. Data from
the home assistant "zone.home" object is used to add the latitude, longitude (and name).
This object also links to relevant devices and features of interest (FoI), but these are added
automatically in a later stage

This steps also allows the creation of Room entities, which can be labeled. A room also allows links to
devices and FoI but these are added later as well. Rooms are automatically linked to the Home {H--(hasRoom)->R}.

*Persons will be added in a later stage*

-- Translate Devices and parse Properties --
The program loops over all devices, which are currently [device_tracker, media_player, sensor, switch].
A property is created for each state of these devices, which are linked to the devices {(D--(observes)-->P) || (D--(actuates)-->P)}
Media players and switches are said to "actuate" their state, whereas device_trackers and sensors "observe" their state.
Attributes may be translated into Property entities manually.

-- Manually create Features of Interest (FoI) -- 
Finally Features of Interest are created and linked to Rooms and Properties. This is done by first listing all
Properties and Devices. First Devices can be linked to Rooms, or the Home. Then FoI can be created, labeled and linked
to specific Properties and/or Rooms or Home.
"""

import json
import copy

import parser.ld_templates as templates
from parser.parser import HALDParser

# -----------------------------------------------------

# Create a Home named MatchBox:
def create_home(label):
    home = copy.copy(templates.TEMPLATE_HOME)
    home['@id'] = 'matchbox_home'
    home['label'] = 'MatchBox'
    return home


# Create Rooms
rooms = []

def create_rooms():
    rooms = []

create_rooms()

# ----------------------------------------------------
# import parser
# from parser import HALDParser
haldp = HALDParser()
devices, properties = haldp.parse()

# ----------------------------------------------------

# Add the device to a specific room
def assign_device_to_room(devices):
    if rooms:
        print('Not yet implemented')

assign_device_to_room(devices)

def print_devices(devices):
    print("---- Devices -----")
    printstring = []
    for dev in devices:
        ps.append(dev)
        if (len(dev) == 3):
            print(ps[0] + '\t' + ps[1] + '\t' + ps[2])
            ps = []
    if(ps): print(ps)
    print("------------------")

def print_properties(properties):
    print("--- Property IDs ---")
    for prop in properties:
        print(prop['@id'])
    print("------------------")

def create_foi(devices, properties):
    print_properties(properties)

    fois = []
    while True:
        q_create = input('Do you want to create a Feature Of Interest? [Y/n]  ')
        if (q_create == 'N' or q_create == 'n'): break
        elif (q_create == 'Y' or q_create == 'y'):
            foi = copy.copy(templates.TEMPLATE_FOI)
            q_label = input('[FoI] label:\t')
            
            props = []
            while True:
                q_add_prop = input('Add property? [Y/n]  ')
                if (q_add_prop == 'N' or q_add_prop == 'n'): break
                elif (q_add_prop == 'Y' or q_add_prop == 'y'):
                    q_prop = input('Enter the property ID: ')
                    if (q_prop in [prop['@id'] for prop in properties]):
                        props.append(q_prop)
                    else:
                        print('Invalid property ID')
                        print_properties(properties)
                else:
                    print('Answer with Y/y or N/n')

            foi['@id'] = q_label
            foi['label'] = q_label
            foi['hasProperty'] = props
            
            fois.append(foi)
        else:
            print('Answer with Y/y or N/n')
    
    if (fois):
        print(json.dumps(fois[0]))


create_foi(devices, properties)
