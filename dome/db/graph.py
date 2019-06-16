import sys, os
sys.path.append(os.path.abspath(os.path.join('lib', 'redland', 'bindings', 'python')))

from RDF import Storage, Model, Uri, NS, Statement, Node

import uuid

import dome.config as config

# Move to config
DOME = NS('http://kadjanderman.com/ontology/')
DOME_DATA = NS('http://kadjanderman.com/resource/')
# These current do not generate valid URIs
rdf = NS('https://www.w3.org/TR/rdf-schema/')
rdfs = rdf

def cleanUri(ha_name):
    ha_name = ha_name.replace('.', '-')
    return ha_name

STORAGE_NAME = 'sqlite'
GRAPH_NAME = 'domegraph.sqlite3'

def singleton(cls):
    return cls()

@singleton
class Graph:
    path = None
    model = None
    
    def __init__(self, path=None):
        if (path):
            self.path = path
        else:
            self.path = os.path.join('.', 'domegraph.sqlite3')
        self._open()

    def _open(self):
        if (self.model is not None):
            return self.model
        # Add try-catch here
        # try:
        if (os.path.isfile(os.path.join('.', 'domegraph.sqlite3'))):
            print('Reusing new store')
            storage = Storage(storage_name=STORAGE_NAME, name=GRAPH_NAME, options_string="new='false'")
        else:
            print('Creating new store')
            storage = Storage(storage_name=STORAGE_NAME, name=GRAPH_NAME, options_string="new='true'")
        self.model = Model(storage)            
        return self.model
        # except Exception:
        print('Storage creation failed')
            # return None
    
    def _add(self, statements):
        for statement in statements:
            self.model.append(statement)
        self.model.sync()
    
    def addDevice(self, label, actuates, prop_src, ha_name, ha_type):
        subject = DOME_DATA[cleanUri(ha_name)]
        statements = [
            Statement(subject, rdf.type, DOME.Device),
            Statement(subject, rdfs.label, label),
            Statement(subject, DOME.ha_name, ha_name),
            Statement(subject, DOME.ha_type, ha_type)
        ]
        assert(isinstance(prop_src, Node))
        if (actuates):
            statements.append(Statement(subject, DOME.actuates, prop_src))
        else:
            statements.append(Statement(subject, DOME.observes, prop_src))
        
        self._add(statements)
        return subject
    
    def addProperty(self, label, value, updated, changed):
        subject = DOME_DATA['property/'+label+str(uuid.uuid4())]
        statements = [
            Statement(subject, rdf.type, DOME.Property),
            Statement(subject, rdfs.label, label),
            Statement(subject, DOME.value, value),
            Statement(subject, DOME.last_updated, updated),
            Statement(subject, DOME.last_changed, changed)
        ]
        self._add(statements)
        return subject
    
    def addAutomation(self, label, trigger, actions, enabled=True):
        subject = DOME_DATA['automation/'+label+str(uuid.uuid4())]
        statements = [
            Statement(subject, rdf.type, DOME.Automation),
            Statement(subject, rdfs.label, label),
            Statement(subject, DOME.triggeredby, DOME.Trigger),
            Statement(subject, DOME.isenabled, enabled)
        ]
        for action in actions:
            statements.append(subject, DOME.performs, actions)
        self._add(statements)
        return subject
    
    def addTrigger(self, label, triggers, conditions, operator):
        subject = DOME_DATA['trigger/'+label+str(uuid.uuid4())]
        statements = [
            Statement(subject, rdf.type, DOME.Trigger),
            Statement(subject, rdfs.label, label),
            Statement(subject, DOME.operatortype, operator)
        ]
        for trigger in triggers:
            statements.append(subject, DOME.hassubtrigger, trigger)
        for condition in conditions:
            statements.append(subject, DOME.hascondition, condition)
        self._add(statements)
        return subject
    
    def addCondition(self, label, prop_src, value, operator):
        subject = DOME_DATA['condition/'+label+str(uuid.uiid4())]
        statements = [
            Statement(subject, rdf.type, DOME.Condition),
            Statement(subject, rdfs.label, label),
            Statement(subject, DOME.observes, prop_src),
            Statement(subject, DOME.target, value),
            Statement(subject, DOME.operatortype, operator)
        ]
        self._add(statements)
        return subject
    
    def addAction(self, label, prop_src, service):
        subject = DOME_DATA['action/'+str(uuid.uuid4())]
        statements = [
            Statement(subject, rdf.type, DOME.Action),
            Statement(subject, rdfs.label, label),
            Statement(subject, DOME.actuates, prop_src),
            Statement(subject, DOME.callservice, command)
        ]
        self._add(statements)
        return subject

    # Removes all existing statements first!!!
    def updateStatement(self, src, pred, obj):
        for stmt in self.model.find_statements(Statement(src, pred, None)):
            del self.model[stmt]
        self.model.append(Statement(src, pred, obj))

    # More adds to be added'
    def getModel(self):
        if (not self.model):
            self._open()
        return self.model
    
    def __del__(self):
        del self.model

if __name__ == "__main__":

    # graph = Graph()
    
    # device_ref = graph.getModel().get_source(DOME.ha_name, 'switch.sonoff')
    # print(device_ref, type(device_ref))
    # for statement in graph.getModel().find_statements(Statement(device_ref, None, None)):
    #     print(statement)
    

    # graph.updateStatement(
    #     Uri('http://kadjanderman.com/resource/property/dda84922-1282-4bc6-b5b1-363b965e8b9a'),
    #     DOME.value,
    #     '50')
    # Graph.addProperty('testproperty', '24', 'yesterday', 'yesterday')
    for statement in Graph.getModel():
        print(statement)

    src = Graph.getModel().get_source(Uri('http://kadjanderman.com/ontology/ha_name'), "switch.sonoff")
    print(['-----']*20)
    src_string = str(src)
    print(src_string, type(src_string))
    uri = Uri(src_string)
    print(uri, type(uri))
    stmts = Graph.getModel().find_statements(Statement(uri, None, None))
    for stmt in stmts:
        print(stmt)
    
    del Graph

