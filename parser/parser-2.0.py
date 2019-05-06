# Built-in modules
import json
import os
import copy

# Installed modules

# Custom modules
import config
import parser.ld_templates as templates

DOME = config.DOME_NAMESPACE

# TODO make separate directories for group, person and zone and parse them separately
WHITELIST = ['switch', 'sensor', 'media_player', 'device_tracker']

class HALDParser():
    fp_in = config.PARSER_IN_DEVICE
    graph = None

    def __init__(self, graph):
        self.graph = graph

    # Function to call when parsing
    def parse(self):
        num_parsed = 0
        for f in self.get_files():
            device_raw = self.load(self.fp_in + f)
            self.parse_device(device_raw)
            num_parsed += 1
        return num_parsed
    
    # Function which parses all devices
    def parse_device(self, device_raw):
        device = copy.copy(templates.TEMPLATE_DEVICE)
        # Check whether the device is an actuator or sensor
        actuator = (str(device_raw['entity_id']).split('.')[0]) in ['media_player', 'switch']
        
        device['@id'] = device_raw['entity_id']
        try:
            device['label'] = device_raw['attributes']['friendly_name']
        except KeyError :
            device['label'] = device_raw['entity_id']

        # Parse the 'state'-property and link to this entity
        property_id = self.parse_property(device_raw)
        if actuator:
            device['actuates'] = property_id
        else:
            device['observes'] = property_id

        
        
        graph.parse(device, format='json-ld')
    
    # Currently only parses states, not attributes
    def parse_property(self, device_raw):
        prop = copy.copy(templates.TEMPLATE_PROPERTY)
        prop['@id'] = device_raw['entity_id'] + "." + 'state'
        prop['label'] = device_raw['entity_id'] + "." + 'state'
        prop['value'] = device_raw['state']
        prop['last_updated'] = device_raw['last_updated']
        prop['last_changed'] = device_raw['last_changed']

        graph.parse(prop, format='json-ld')

        return prop['@id']

    # Returns a list of files which can be parsed by this parser
    def get_files(self):
        res = []
        for f in os.listdir(self.fp_in):
            precursor = (str(f).split('.'))[0]
            if (precursor in WHITELIST):
                res.append(f)
        return res

    # Returns a json object obtained from a file
    def load(self, fp):
        device = None
        with open(fp, 'r') as f:
            device = json.load(f)
        return device