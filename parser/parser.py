# Built-in modules
import json
import os
import copy

# Installed modules

# Custom modules
import config
import parser.ld_templates as templates

# TODO make separate directories for group, person and zone and parse them separately
WHITELIST = ['switch', 'sensor', 'media_player', 'device_tracker']

class HALDParser():
    devices, properties = [], []
    fp_in = config.PARSER_IN_DEVICE
    # fp_out = config.PARSER_OUT_DEVICE
    device_out = config.KB_DEVICE
    property_out = config.KB_PROPERTY
    graph = None

    def __init__(self, graph=None):
        self.graph = graph

    # Function to call when parsing
    def parse(self):
        self.devices, self.properties = [], []
        for f in self.get_files():
            device_raw = self.load(self.fp_in + f)
            self.parse_device(device_raw)
        return (self.devices, self.properties)
    
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
        
        self.devices.append(device)
        self.store_entity(device, self.device_out)
        if(self.graph):
            graph.parse(device, format='json-ld')
    
    # Currently only parses states, not attributes
    def parse_property(self, device_raw):
        prop = copy.copy(templates.TEMPLATE_PROPERTY)
        prop['@id'] = device_raw['entity_id'] + "." + 'state'
        prop['label'] = device_raw['entity_id'] + "." + 'state'
        prop['value'] = device_raw['state']
        prop['last_updated'] = device_raw['last_updated']
        prop['last_changed'] = device_raw['last_changed']
        self.properties.append(prop)
        self.store_entity(prop, self.property_out)

        if(self.graph):
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

    # Stores a json object to a file
    def store_entity(self, entity, path):
        fp = path + entity['@id']
        with open(fp, 'w') as f:
            json.dump(entity, f, indent=4)