import os
import dome.config as config
import uuid

from rdflib import plugin, Graph, RDF, RDFS, URIRef, Literal
from rdflib.store import NO_STORE, VALID_STORE, Store
from bsddb3.db import DBNoSuchFileError

DOME = config.DOME_NAMESPACE
DOME_DATA = config.DOME_DATA_NAMESPACE

class KnowledgeGraph():
    ident = URIRef("domeld")
    graph = None
    path = None

    def __init__(self, store_path=config.PATH_SLEEPYCAT):
        self.path = store_path
        self.openGraph()
        if (os.path.isfile(store_path)):
            self.graph.parse(store_path, format='turtle')
    
    def remove(self, entity, field, value):
        self.openGraph()
        self.graph.remove( (URIRef(entity), field, value) )

    # -----------------  Creation of home context triples  --------------
    
    def add_device(self, label, actuates, property_ref, ha_name, ha_type):

        subject = DOME_DATA['device/'+str(uuid.uuid4())]
        
        self.openGraph()

        self.graph.add( (subject, RDF.type, DOME.Device) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        if(actuates):
            self.graph.add( (subject, DOME.actuates, property_ref) )
        else:
            self.graph.add( (subject, DOME.observes, property_ref) )
        self.graph.add( (subject, DOME.homeassistantname, Literal(ha_name)) )
        self.graph.add( (subject, DOME.homeassistanttype, Literal(ha_type)) )

        self.closeGraph()
        return subject

    def add_property(self, label, value, updated, changed):
        subject = DOME_DATA['property/'+str(uuid.uuid4())]

        self.openGraph()

        self.graph.add( (subject, RDF.type, DOME.Property) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        self.graph.add( (subject, DOME.value, Literal(value)) )
        self.graph.add( (subject, DOME.last_updated, Literal(updated)) )
        self.graph.add( (subject, DOME.last_changed, Literal(changed)) )

        self.closeGraph()
        return subject
    
    def add_home(self, label):
        subject = DOME_DATA['home/'+str(uuid.uuid4())]

        self.openGraph()

        self.graph.add( (subject, RDF.type, DOME.Home) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )

        self.closeGraph()
        return subject
    
    def add_room(self, label, home):
        subject = DOME_DATA['room/'+str(uuid.uuid4())]

        self.openGraph()

        self.graph.add( (subject, RDF.type, DOME.Room) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        self.graph.add( (subject, DOME.partOf, URIRef(home)))

        self.closeGraph()
        return subject
    
    def add_foi(self, label, location, properties):
        subject = DOME_DATA['foi/'+str(uuid.uuid4())]

        self.openGraph()

        self.graph.add( (subject, RDF.type, DOME.FeatureOfInterest) )
        self.graph.add( (subject, RDFS.label, Literal(label)) )
        self.graph.add( (DOME_DATA[location], DOME.hasfeatureofinterest, subject) )
        for prop in properties:
            self.graph.add( (subject, DOME.hasproperty, URIRef(prop)) )
        
        self.closeGraph()
        return subject

    # -----------------  Modification of triples --------------------------

    def modify_literal(self, entity_id, pred, value):
        self.openGraph()
        self.graph.set( (URIRef(entity_id), pred, Literal(value)) )
        self.closeGraph()
        return 
    
    def modify_ref(self, entity_id, pred, value):
        self.openGraph()
        self.graph.set( (URIRef(entity_id), pred, URIRef(value)) )
        self.closeGraph()
        return 

    # ---------------------- Persistent Store Fucntion ------------------
    def openGraph(self):
        self.graph = Graph('Sleepycat', identifier=self.ident)
        rt = None
        try:
            rt = self.graph.open(self.path, create=False)
        except DBNoSuchFileError:
            rt = self.graph.open(self.path, create=True)
        
        if rt == NO_STORE:
            # There is no underlying sleepycat infrstructure
            self.graph.open(self.path, create=True)
        else:
            assert rt == VALID_STORE, 'The underlying store is corrupt'
    
    def closeGraph(self):
        if (self.graph):
            self.graph.close()
        self.graph = None

    # ------------  store: required after every update ------------------

    # Load the store with triples from a turtle file
    def load(self, path=None):
        self.openGraph()
        if(not path):
            path = self.path
        self.graph.parse(path, format='turtle')
        self.closeGraph()

    def writeToFile(self, path):
        self.openGraph()
        assert path != self.path, 'Cannot overwrite db'
        self.graph.serialize(destination=path, format='turtle')
        self.closeGraph()

    # --------------------------  Getters --------------------------------
    
    def get_entity(self, subj=None, pred=None, obj=None, isURI=True):
        self.openGraph()
        if (obj):
            if(isURI):
                obj = URIRef(obj)
            else:
                obj = Literal(obj)
        entity = list(self.graph[subj:pred:obj])
        self.closeGraph()
        return entity

    # Retrieves a single entity with all it's properties
    def get_entity_by_id(self, entity_id, mode=0):
        self.openGraph()
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
        self.closeGraph()
        return ret
    
    # Retrieve all entities
    # Modes: 0=only ids, 1=only labels, 2=all data
    def get_entities_by_type(self, t, mode=0):
        self.openGraph()
        ret = None
        entities_id = list(self.graph[:RDF.type:t])
        if (mode == 0):
            ret = entities_id
        elif (mode == 1):
            ret = [str(list(self.graph[subj:RDFS.label:])[0]) for subj in entities_id]
        elif (mode == 2):
            ret = [self.get_entity_by_id(entity) for entity in entities_id]
        else:
            print("mode '"+str(mode)+"' not valid")
        self.closeGraph()
        return ret
    
    # --------------- Purge: removes the triple store(!!) ----------------

    # Removes the graph, both in memory and in file.
    def purge(self):
        if(os.path.isdir(self.path)):
            for f in os.listdir(self.path):
                file_path = os.path.join(self.path, f)
                try:
                    if (os.path.isfile(file_path)):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
    
    def __str__(self):
        self.openGraph()
        string = str(self.graph.serialize())
        self.closeGraph()
        return string

    def __len__(self):
        self.openGraph()
        length = len(self.graph)
        self.closeGraph()
        return length


if __name__ == "__main__":
    kg = KnowledgeGraph()