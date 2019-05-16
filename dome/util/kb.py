import os
import dome.config as config
import uuid

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
    
    def remove(self, entity, field, value):
        self.graph.remove( (URIRef(entity), field, value) )

    # -----------------  Creation of home context triples  --------------
    
    def add_device(self, label, actuates, property_ref):
        subject = DOME_DATA['device/'+str(uuid.uuid4())]
        
        self.graph.add( (subject, RDF.type, DOME.Device) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        if(actuates):
            self.graph.add( (subject, DOME.actuates, property_ref) )
        else:
            self.graph.add( (subject, DOME.observes, property_ref) )
        self.store()
        return subject

    def add_property(self, label, value, updated, changed):
        subject = DOME_DATA['property/'+str(uuid.uuid4())]

        self.graph.add( (subject, RDF.type, DOME.Property) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        self.graph.add( (subject, DOME.value, Literal(value)) )
        self.graph.add( (subject, DOME.last_updated, Literal(updated)) )
        self.graph.add( (subject, DOME.last_changed, Literal(changed)) )
        self.store()
        return subject
    
    def add_home(self, label):
        subject = DOME_DATA['home/'+str(uuid.uuid4())]
        self.graph.add( (subject, RDF.type, DOME.Home) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        self.store()
        return subject
    
    def add_room(self, label):
        subject = DOME_DATA['room/'+str(uuid.uuid4())]
        self.graph.add( (subject, RDF.type, DOME.Room) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        self.store()
        return subject
    
    def add_foi(self, label, location, properties):
        subject = DOME_DATA['foi/'+str(uuid.uuid4())]
        self.graph.add( (subject, RDF.type, DOME.FeatureOfInterest) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        self.graph.add( (DOME_DATA[location], DOME.hasfeatureofinterest, subject) )
        for prop in properties:
            self.graph.add( (subject, DOME.hasproperty, URIRef(prop)) )
        self.store()
        return subject

    # -----------------  Modification of triples --------------------------

    def modify_literal(self, entity_id, pred, value):
        self.graph.set( (URIRef(entity_id), pred, Literal(value)) )
        self.store()
        return 
    
    def modify_ref(self, entity_id, pred, value):
        self.graph.set( (URIRef(entity_id), pred, URIRef(value)) )
        self.store()
        return 
    
    def modify_literal_m(self, entity_id, pred, values):
        return self.graph[URIRef(entity_id):pred:]

    # ------------  store: required after every update ------------------

    def load(self, path=None):
        if(not path):
            path = self.path
        self.graph.parse(path, format='turtle')

    def store(self, path=None):
        if(not path):
            path = self.path
        self.graph.serialize(destination=path, format='turtle')

    # --------------------------  Getters --------------------------------
    
    # obj=(id, isURI)
    def get_entity(self, subj=None, pred=None, obj=None, isURI=True):
        # if (entity1 == pred == entity2 == None):
        #     return None
        if (obj):
            if(isURI):
                obj = URIRef(obj)
            else:
                obj = Literal(obj)
        return list(self.graph[subj:pred:obj])

    # Retrieves a single entity with all it's properties
    def get_entity_by_id(self, entity_id, mode=0):
        if (mode == 1):
            return str(list(self.graph[URIRef(entity_id):RDFS.label:])[0])
        ret = {'id': str(entity_id)}
        for prop in list(self.graph[URIRef(entity_id)::]):

            # If multiple objects share a predicate, store as list
            if (str(prop[0]) in ret):
                if (not isinstance(ret[str(prop[0])], list)):
                    ret[str(prop[0])] = [ret[str(prop[0])]]
                ret[str(prop[0])].append(str(prop[1]))
            else:
                ret[str(prop[0])] = str(prop[1])
        return ret
    
    # Retrieve all entities
    # Modes: 0=only ids, 1=only labels, 2=all data
    def get_entities_by_type(self, t, mode=0):
        entities_id = list(self.graph[:RDF.type:t])
        if (mode == 0):
            return entities_id
        elif (mode == 1):
            return [str(list(self.graph[subj:RDFS.label:])[0]) for subj in entities_id]
        elif (mode == 2):
            return [self.get_entity_by_id(entity) for entity in entities_id]
        
        print("mode '"+str(mode)+"' not valid")
        return None
    
    # --------------- Purge: removes the triple store(!!) ----------------

    # Removes the graph, both in memory and in file.
    def purge(self):
        if(os.path.isfile(config.PATH_STORE)):
            os.remove(config.PATH_STORE)
        self.graph = Graph()
    
    def __str__(self):
        return str(self.graph.serialize())

    def __len__(self):
        return len(self.graph)


if __name__ == "__main__":
    kg = KnowledgeGraph()