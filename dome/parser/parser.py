# Built-in modules
import json
import os
import copy

# Installed modules
from rdflib.namespace import RDF, RDFS
from rdflib import Literal

# Custom modules
import dome.config as config
from dome.util.kb import KnowledgeGraph

DOME = config.DOME_NAMESPACE
DOME_DATA = config.DOME_DATA_NAMESPACE

WHITELIST = ['switch', 'sensor', 'media_player', 'device_tracker']

class HALDParser():
    fp_in = config.PARSER_IN_DEVICE
    graph = None

    def __init__(self, graph, fp_in=config.PARSER_IN_DEVICE):
        self.graph = graph
        self.fp_in = fp_in

    # Function to call when parsing
    def parse(self):
        num_parsed = 0
        for f in self.get_files():
            device_raw = self.load(self.fp_in + f)
            self.parse_device(device_raw)
            num_parsed += 1
            
        self.graph.commit()
        return num_parsed
    
    # Function which parses all devices
    def parse_device(self, device_raw):
        label, actuates, observes = None, None, None

        # Check whether the device is an actuator or sensor
        actuator = (str(device_raw['entity_id']).split('.')[0]) in ['media_player', 'switch']

        # A friendly name is preferred over an entity id as label
        try:
            label = device_raw['attributes']['friendly_name']
        except KeyError :
            label = device_raw['entity_id']
        
        # Parse the 'state'-property and link to this entity
        prop_ref = self.parse_property(device_raw)

        # Finally add the device to the graph
        self.graph.add_device(label, actuator, prop_ref)
    
    # Currently only parses states, not attributes
    def parse_property(self, device_raw):
        prop_ref = self.graph.add_property(device_raw['entity_id'], device_raw['state'], 
            device_raw['last_updated'], device_raw['last_changed'])
        return prop_ref

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

if __name__ == "__main__":
    graph = KnowledgeGraph()
    parser = HALDParser(graph)
    parser.parse()