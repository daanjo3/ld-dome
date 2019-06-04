from SPARQLWrapper import SPARQLWrapper, JSON

def makeQuery(resource, field):
    query = """
    SELECT ?value WHERE {
        <%s> <%s> ?value
    }
    """ % (resource, field)
    return query

class WebUpdater():
    sparql = None
    value = None

    def __init__(self, host, query, graph=None):
        self.sparql = SPARQLWrapper(host, returnFormat=JSON, defaultGraph=graph)
        self.sparql.setQuery(query)
        self.update()
    
    # Single values only!
    def update(self):
        result = (self.sparql.query().convert())['results']['bindings'][0]['value']
        self.value = result['value']
        if (result['type'] == 'typed-literal'):
            if (result['datatype'] == 'http://www.w3.org/2001/XMLSchema#integer'):
                self.value = int(result['value'])
        return self.value

remote = WebUpdater(
    'http://localhost:8890/sparql',
    makeQuery('http://example.org/princenhageweather', 'http://example.org/ns#precipitation'),
    graph='urn:graph:dummy:princenhage')