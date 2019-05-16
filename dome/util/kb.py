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
    
    def remove(self, entity, field, value):
        self.graph.remove( (URIRef(entity), field, value) )
    
    # TODO replace ID creation to within KB
    def add_device(self, device_id, label, actuates, property_ref):
        subject = DOME_DATA[device_id]
        self.graph.add( (subject, RDF.type, DOME.Device) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        if(actuates):
            self.graph.add( (subject, DOME.actuates, property_ref) )
        else:
            self.graph.add( (subject, DOME.observes, property_ref) )
        return subject

    # TODO replace ID creation to within KB
    def add_property(self, property_id, label, value, updated, changed):
        subject = DOME_DATA[property_id]
        self.graph.add( (subject, RDF.type, DOME.Property) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        self.graph.add( (subject, DOME.value, Literal(value)) )
        self.graph.add( (subject, DOME.last_updated, Literal(updated)) )
        self.graph.add( (subject, DOME.last_changed, Literal(changed)) )
        return subject
    
    # TODO replace ID creation to within KB
    def add_home(self, home_id, label):
        subject = DOME_DATA[home_id]
        self.graph.add( (subject, RDF.type, DOME.Home) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        return subject
    
    # TODO replace ID creation to within KB
    def add_room(self, room_id, label):
        subject = DOME_DATA[room_id]
        self.graph.add( (subject, RDF.type, DOME.Room) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        return subject
    
    def add_foi(self, label, location, properties):
        subject = self.get_valid_id(DOME_DATA['foi/'+label])
        self.graph.add( (subject, RDF.type, DOME.FeatureOfInterest) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        self.graph.add( (DOME_DATA[location], DOME.hasfeatureofinterest, subject) )
        for prop in properties:
            self.graph.add( (subject, DOME.hasproperty, URIRef(prop)) )
        return subject

    def modify(self, entity, pred, value, isLiteral=True):
        subj = URIRef(entity)
        obj = None
        if(isLiteral):
            obj = Literal(value)
        else:
            obj = URIRef(value)
        if((subj, pred, None) in self.graph):
            self.graph.set( (subj, pred, obj) )

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
    
    def get_entity(self, entity_id):
        # print('------ GET ENTITY -----')
        ret = {'id': str(entity_id)}
        # print(str(entity_id))
        for prop in list(self.graph[URIRef(entity_id)::]):
            # print(prop)
            if (str(prop[0]) in ret):
                if (not isinstance(ret[str(prop[0])], list)):
                    ret[str(prop[0])] = [ret[str(prop[0])]]
                ret[str(prop[0])].append(str(prop[1]))
            else:
                ret[str(prop[0])] = str(prop[1])
        # print(ret)
        return ret
    
    def get_entities_by_type(self, t):
        entities = []
        for entity in self.list_by_type(t):
            entities.append(self.get_entity(entity))
        return entities

    def get_valid_id(self, entity_id):
        new_id = entity_id
        i = 1
        while(self.has_id(new_id)):
            new_id = entity_id+'/'+str(i)
            i += 1
        return new_id

    def has_id(self, entity_id):
        return (entity_id, None, None) in self.graph
    
    def clear(self):
        self.graph = None
        if(os.path.isfile(config.PATH_STORE)):
            os.remove(config.PATH_STORE)
    
    def __str__(self):
        return str(self.graph.serialize())

    def __len__(self):
        return len(self.graph)


if __name__ == "__main__":
    kg = KnowledgeGraph()