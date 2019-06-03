from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json

import dome.config as config
from dome.util.kb import KnowledgeGraph
from dome.util import cli_configure

DOME = config.DOME_NAMESPACE
from rdflib import RDFS

types = [
    {'name': 'Home', 'value': DOME.Home},
    {'name': 'Room', 'value': DOME.Room},
    {'name': 'Device', 'value': DOME.Device},
    {'name': 'Property', 'value': DOME.Property},
    {'name': 'Feature of Interest', 'value': DOME.FeatureOfInterest}
]

SCREEN_MAIN = [
    {
        'type': 'list',
        'name': 'menu_option',
        'message': 'Main Menu',
        'choices': ['Configure', 'Status', 'Exit']
    }
]

SCREEN_STATUS_MAIN = [
    {
        'type': 'list',
        'name': 'menu_option',
        'message': 'Status',
        'choices': ['List all', 'List by type', 'Show entity', 'Return']
    }
]

SCREEN_STATUS_TYPE = [
    {
        'type': 'list',
        'name': 'menu_option',
        'message': 'Entity types',
        'choices': types + [{'name': 'Return', 'value': 'Return'}]
    }
]

def status_print_type(t_label, t):
    if (t == DOME.Property):
        entity_list = KnowledgeGraph.get_entities_by_type(t, mode=2)
        print('----- {} -----'.format(t_label))
        for entity in entity_list:
            print("{:<35}: {}".format(entity[str(RDFS.label)], entity[str(DOME.value)]))
            print("{}\n".format(entity['id']))
        print()
    else:
        entity_list = KnowledgeGraph.get_entities_by_type(t, mode=2)
        print('----- {} -----'.format(t_label))
        for entity in entity_list:
            print(entity['id'])
            print('{}\n'.format(entity[str(RDFS.label)]))

def status_list_all():
    cli_configure.clear()
    for t in types:
        status_print_type(t['name'], t['value'])

def status_list_by_type(t_value):
    cli_configure.clear()
    label = ""
    for t in types:
        if (t['value'] == t_value):
            label = t['name']
    status_print_type(label, t_value)


def status_menu_type():
    cli_configure.clear()
    while(True):
        option = prompt(SCREEN_STATUS_TYPE)['menu_option']
        if (option == 'Return'):
            break;
        else:
            status_list_by_type(option)
            

def status_menu_main():
    cli_configure.clear()
    while(True):
        option = prompt(SCREEN_STATUS_MAIN)['menu_option']
        if (option == 'List all'):
            status_list_all()
        if (option == 'List by type'):
            status_menu_type()
        if (option == 'Return'):
            break;

def main():
    while(True):
        option = prompt(SCREEN_MAIN)['menu_option']
        if (option == 'Configure'):
            cli_configure.config_main()
        if (option == 'Status'):
            status_menu_main()
        if (option == 'Exit'):
            return;

if __name__ == "__main__":
    main()