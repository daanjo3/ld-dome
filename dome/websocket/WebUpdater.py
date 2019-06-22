# built-in import
import time
from multiprocessing import Process

# SPARQLWrapper import
from SPARQLWrapper import SPARQLWrapper, JSON

# DomeLD import
from dome.db.graph import Graph
from dome.lib.state import BaseState
from dome.lib.observable import Observable
from dome.parser.ParserService import Origin
from dome.config import DOME, rdf

HOUR = 60 * 60

class State(BaseState):
    pass

class SPARQLService():
    sparql = None

    def __init__(self, host, query, graph=None):
        self.sparql = SPARQLWrapper(host, returnFormat=JSON, defaultGraph=graph)
        self.sparql.setQuery(query)
    
    # Single values only!
    def update(self):
        result = (self.sparql.query().convert())['results']['bindings'][0]
        value = result['value']
        if (value['type'] == 'typed-literal'):
            if (value['datatype'] == 'http://www.w3.org/2001/XMLSchema#integer'):
                return int(value['value'])

class WebUpdater(Process, Observable):
    state = State()
    services = []

    def __init__(self, dome):
        Process.__init__(self)
        Observable.__init__(self)
        self.queue = dome.parser_queue
        self.kb_readable = dome.graph_readable_event
    
    def awakeService(self):
        awaken = []
        for service in self.services:
            if (self.serviceSleep(service) <= 0):
                awaken.append(service)
        return awaken

    def serviceSleep(self, service):
        sleep_seconds = service['poll'] * 60
        wait_time = service['last_updated'] + sleep_seconds - time.time()
        return wait_time

    def waitTime(self):
        times = []
        for service in self.services:
            times.append(self.serviceSleep(service))
        if (len(times) >= 1):
            return min(times)
        else:
            return HOUR
    
    def run(self):
        self.kb_readable.wait()
        self.loadWebResources()
        try:
            while True:
                wait = self.waitTime()
                if (wait > 0):
                    time.sleep(self.waitTime())
                for service in self.awakeService():
                    self.query(service)
        except KeyboardInterrupt:
            return
    
    # TODO compare for last_changed
    def query(self, service):
        value = service['sparql'].update()
        print(value)
        service['last_updated'] = time.time()
        if (value is None):
            return
        payload = ({
            'id': str(service['prop_ref']),
            'last_updated': time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime()),
            'state': value
        })
        self.queue.put((Origin.WEB_UPDATER, payload))

    def loadWebResources(self):
        webproperties = Graph.getModel().get_sources(rdf.type, DOME.WebProperty)
        for wp in webproperties:
            res = Graph.getModel().get_target(wp, DOME.resource)
            prop = Graph.getModel().get_target(wp, DOME.property)
            host = Graph.getModel().get_target(wp, DOME.hostedby)
            graphname = Graph.getModel().get_target(wp, DOME.graphname)
            graphname = str(graphname) if graphname else None

            query = formulateQuery(str(res), str(prop))
            sparql = SPARQLService(str(host), query, graph=graphname)
            
            poll = Graph.getModel().get_target(wp, DOME.poll)
            self.services.append({
                'prop_ref': wp,
                'sparql': sparql,
                'poll': int(str(poll)),
                'last_updated': 0,
            })

    def update(self, state):
        self.state.update(state)
        self.notify('[{}] {}'.format(self.name, self.state))

def formulateQuery(resource, field):
    query = """
        SELECT ?value WHERE {
        <%s> <%s> ?value
        }
    """ % (resource, field)
    return query