import os
import dome.config as config

from rdflib import Graph, RDF, RDFS, URIRef, Literal

DOME = config.DOME_NAMESPACE
DOME_DATA = config.DOME_DATA_NAMESPACE

class KnowledgeGraph():
    graph = Graph()
    path = None

    def __init__(self, store_path=config.PATH_STORE):        
        self.path = store_path
        if (os.path.isfile(store_path)):
            self.graph.parse(store_path, format='turtle')
    
    def add(self, s, p, o):
        self.graph.add( (s, p, o) )
    
    def add_device(self, device_id, label, actuates, property_ref):
        subject = DOME_DATA[device_id]
        self.graph.add( (subject, RDF.type, DOME.Device) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        if(actuates):
            self.graph.add( (subject, DOME.actuates, property_ref) )
        else:
            self.graph.add( (subject, DOME.observes, property_ref) )
        return subject

    def add_property(self, property_id, label, value, updated, changed):
        subject = DOME_DATA[property_id]
        self.graph.add( (subject, RDF.type, DOME.Property) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        self.graph.add( (subject, DOME.value, Literal(value)) )
        self.graph.add( (subject, DOME.last_updated, Literal(updated)) )
        self.graph.add( (subject, DOME.last_changed, Literal(changed)) )
        return subject
    
    def add_home(self, home_id, label):
        subject = DOME_DATA[home_id]
        self.graph.add( (subject, RDF.type, DOME.Home) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        return subject

    def commit(self, path=None):
        if(not path):
            path = self.path
        self.graph.serialize(destination=path, format='turtle')

    def list_by_type(self, t, label=False):
        subj_list = list(self.graph[:RDF.type:t])
        if(label):
            label_list = []
            for subj in subj_list:
                label = str(list(self.graph[subj:RDFS.label:])[0])
                label_list.append(label)
            return label_list
        return subj_list
    
    def clear(self):
        if(os.path.isfile(config.PATH_STORE)):
            os.remove(config.PATH_STORE)
    
    def __str__(self):
        return str(self.graph.serialize())

    def __len__(self):
        return len(self.graph)


if __name__ == "__main__":
    kg = KnowledgeGraph()