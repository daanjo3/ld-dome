# built-in import
import time
from multiprocessing import Process

# SPARQLWrapper import
from SPARQLWrapper import SPARQLWrapper, JSON

# DomeLD import
from dome.lib.state import BaseState
from dome.lib.observable import Observable
from dome.parser.ParserService import Origin
from dome.config import DOME

class State(BaseState):
    pass

class SPARQLService():
    sparql = None
    timeout = 1000 * 60

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
        return min(times)
    
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
            'id': service['prop_ref'],
            'last_updated': time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime()),
            'state': value
        })
        self.queue.put((Origin.WEB_UPDATER, payload))

    def loadWebResources(self):
        webproperties = KnowledgeGraph.get_entities_by_type(DOME.WebProperty, mode=2)
        for wp in webproperties:
            graphname = None
            if (str(DOME.graphname) in wp.keys()):
                graphname = wp[str(DOME.graphname)]
            
            query = formulateQuery(wp[str(DOME.resource)], wp[str(DOME.property)])
            sparql = SPARQLService(wp[str(DOME.hostedby)], query, graph=graphname)
            
            self.services.append({
                'prop_ref': wp['id'],
                'sparql': sparql,
                'poll': int(wp[str(DOME.poll)]),
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