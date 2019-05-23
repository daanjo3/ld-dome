from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json

import dome.config as config
from dome.util.kb import KnowledgeGraph

DOME = config.DOME_NAMESPACE
from rdflib import RDFS

graph = KnowledgeGraph()

def clear():
    import subprocess, platform

    if platform.system()=="Windows":
        subprocess.Popen("cls", shell=True).communicate() #I like to use this instead of subprocess.call since for multi-word commands you can just type it out, granted this is just cls and subprocess.call should work fine 
    else: #Linux and Mac
        print("\033c", end="")

SCREEN_CONFIG_MAIN = [
    {
        'type': 'list',
        'name': 'menu_option',
        'message': 'Configure Menu',
        'choices': ['Add entities', 'Modify entities', 'Remove entities', 'Return']
    }
]

SCREEN_ADD = [
    {
        'type': 'list',
        'name': 'menu_option',
        'message': 'Add Entities',
        'choices': ['add Home', 'add Room', 'add Feature of Interest', 'Return']
    }
]

SCREEN_ADD_HOME = [
    {
        'type': 'input',
        'name': 'label',
        'message': 'Home name'
    }
]

SCREEN_ADD_ROOM = [
    {
        'type': 'input',
        'name': 'label',
        'message': 'Room name'
    },
    {
        'type': 'list',
        'name': 'partOf',
        'message': 'Room location',
        'choices': []
    }
]
def set_add_room():
    home_list = graph.get_entities_by_type(DOME.Home, mode=2)
    SCREEN_ADD_ROOM[1]['choices'] = [{
        'name': home[str(RDFS.label)],
        'value': home['id']
    } for home in home_list]
    if (home_list == []):
        SCREEN_ADD_ROOM[1]['choices'] = ['None']

SCREEN_ADD_FOI = [
    {
        'type': 'input',
        'name': 'label',
        'message': 'Feature of Interest name'
    },
    {
        'type': 'list',
        'name': 'locatedIn',
        'message': 'Feature of Interest location',
        'choices': []
    },
    {
        'type': 'checkbox',
        'name': 'hasProperty',
        'message': 'Feature of Interest properties',
        'choices': []
    }
]
def set_add_foi():
    loc_list = graph.get_entities_by_type(DOME.Home, mode=2) + graph.get_entities_by_type(DOME.Room, mode=2)
    prop_list = graph.get_entities_by_type(DOME.Property, mode=2)

    SCREEN_ADD_FOI[1]['choices'] = [{
        'name': loc[str(RDFS.label)],
        'value': loc['id']
    } for loc in loc_list]
    if (loc_list == []): SCREEN_ADD_FOI[1]['choices'] = ['None']
    
    SCREEN_ADD_FOI[2]['choices'] = [{
        'name': prop[str(RDFS.label)],
        'value': prop['id']
    } for prop in prop_list]
    if (prop_list == []): SCREEN_ADD_FOI[2]['choices'] = ['None']

# ----------------------------------------------------------------- #
# --------------------------  CLI FLOW  --------------------------- #
# ----------------------------------------------------------------- #

def config_main():
    clear()
    while(True):
        option = prompt(SCREEN_CONFIG_MAIN)['menu_option']
        if (option == 'Add entities'):
            config_add_entities()
        if (option == 'Return'):
            break;

def config_add_entities():
    clear()
    while(True):
        option = prompt(SCREEN_ADD)['menu_option']
        if (option == 'add Home'):
            clear()
            config_add_home()
        if (option == 'add Room'):
            clear()
            config_add_room()
        if (option == 'add Feature of Interest'):
            clear()
            config_add_foi()
        if (option == 'Return'):
            break;

def config_add_home():
    answer = prompt(SCREEN_ADD_HOME)
    graph.add_home(answer['label'])
    print(answer)

def config_add_room():
    set_add_room()
    answer = prompt(SCREEN_ADD_ROOM)
    graph.add_room(answer['label'], answer['partOf'])
    print(answer)

def config_add_foi():
    set_add_foi()
    answer = prompt(SCREEN_ADD_FOI)
    graph.add_foi(answer['label'], answer['locatedIn'], answer['hasProperty'])
    print(answer)

if __name__ == "__main__":
    config_main()