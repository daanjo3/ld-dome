import uuid
import json

from rdflib import Graph, plugin
from rdflib.serializer import Serializer

import sys, os
sys.path.append(os.path.abspath(os.path.join('lib', 'redland', 'bindings', 'python')))

from RDF import NS, TurtleParser, Uri
DOME = NS('http://kadjanderman.com/ontology/')
DOME_DATA = NS('http://kadjanderman.com/resource/')

from dome.db.graph import Graph as DGraph

CONTEXT = {
    "@vocab": "http://kadjanderman.com/ontology/",
    "label": "http://www.w3.org/2000/01/rdf-schema#label"
}

class AutomationParser():
    parsed_json = None

    def start(self, automation_raw):
        self.parsed_json = []
        self.parseAutomation(automation_raw)
        g = Graph()
        for part in self.parsed_json:
            g.parse(data=json.dumps(part), format='json-ld')
        automation_string = (g.serialize(format='turtle')).decode('utf-8')
        tp = TurtleParser()
        DGraph.getModel().add_statements(tp.parse_string_as_stream(automation_string, Uri('http://kadjanderman.com/ontology/')))

    def parseCondition(self, condition):
        label = condition["label"]
        ident = str(DOME_DATA['condition/'+str(uuid.uuid4())])
        condition["@context"] = CONTEXT
        condition["@id"] = ident
        condition["@type"] = str(DOME.Condition)
        self.parsed_json.append(condition)
        return {"@id": ident}


    def parseTrigger(self, trigger):
        trigger["hassubtrigger"] = [self.parseTrigger(t) for t in trigger["hassubtrigger"]]
        trigger["hascondition"] = [self.parseCondition(c) for c in trigger["hascondition"]]

        label = trigger["label"]
        ident = str(DOME_DATA['trigger/'+str(uuid.uuid4())])
        trigger["@context"] = CONTEXT
        trigger["@id"] = ident
        trigger["@type"] = str(DOME.Trigger)
        self.parsed_json.append(trigger)
        return {"@id": ident}
        
    def parseAutomation(self, automation):
        automation["triggeredby"] = self.parseTrigger(automation["triggeredby"])
        automation["performs"] = [self.parseAction(a) for a in automation["performs"]]

        label = automation["label"]
        automation["@context"] = CONTEXT
        automation["@id"] = str(DOME_DATA['automation/'+str(uuid.uuid4())])
        automation["@type"] = str(DOME.Automation)
        self.parsed_json.append(automation)
        return

    def parseAction(self, action):
        label = action["label"]
        ident = str(DOME_DATA['action/'+str(uuid.uuid4())])
        action["@context"] = CONTEXT
        action["@id"] = ident
        action["@type"] = str(DOME.Action)
        self.parsed_json.append(action)
        return {"@id": ident}
    

if __name__ == "__main__":
    automation = None
    ap = AutomationParser()
    with open('./automations/automation01.json', 'r') as f:
        automation_raw = json.load(f)
        ap.start(automation_raw)
    with open('./automations/automation02.json', 'r') as f:
        automation_raw = json.load(f)
        ap.start(automation_raw)