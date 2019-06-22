# Redland import
from RDF import Query, Uri

# DomeLD import
from dome.db.graph import Graph
from dome.config import DOME, DOME_DATA, rdf, rdfs

def getWatchlistCondition(condition):
    return Graph.getModel().get_target(condition, DOME.observes)

def getWatchlistTrigger(trigger):
    properties = []
    subtriggers = Graph.getModel().get_targets(trigger, DOME.hassubtrigger)
    conditions = Graph.getModel().get_targets(trigger, DOME.hascondition)
    for st in subtriggers:
        properties += getWatchlistTrigger(st)
    properties += [getWatchlistCondition(c) for c in conditions]
    return properties

def getWatchlist():
    watchlist = []
    automations = Graph.getModel().get_sources(rdf.type, DOME.Automation)
    for automation in automations:
        properties = getWatchlistTrigger(Graph.getModel().get_target(automation, DOME.triggeredby))
        enabled = Graph.getModel().get_target(automation, DOME.isenabled)
        for prop in properties:
            watchlist.append({
                'automation_id': automation,
                'prop_ref': prop,
                'enabled': bool(str(enabled))
            })
    return watchlist

def pre_validate(truths, op):
    if (op == 'AND' and False in truths):
        return False
    if (op == 'OR' and True in truths):
        return True
    return None

def validate(truths, op):
    if (len(truths) == 1):
        if (op == 'NEG'):
            return not truths[0]
        else:
            return truths[0]
    if (op == 'AND'):
        return all(truths)
    if (op == 'OR'):
        return any(truths)
    print('ResolverError: No operator specified for trigger')
    return None

def compare(value, op, target):
    if (op == 'EQ'):
        return str(value) == str(target)
    # TODO extend for multiple datatypes and operators

def verifyCondition(condition):
    target = Graph.getModel().get_target(condition, DOME.target)
    operator = str(Graph.getModel().get_target(condition, DOME.operatortype))
    prop = Graph.getModel().get_target(condition, DOME.observes)
    value = Graph.getModel().get_target(Uri(str(prop)), DOME.value)
    return compare(value, operator, target)

def verifyTrigger(trigger):
    truth = []
    operator = str(Graph.getModel().get_target(trigger, DOME.operatortype))
    subtriggers = Graph.getModel().get_targets(trigger, DOME.subtriggers)
    conditions = Graph.getModel().get_targets(trigger, DOME.hascondition)
    for c in conditions:
        truth.append(verifyCondition(c))
        valid = pre_validate(truth, operator)
        if (valid == True):
            return True
        if (valid == False):
            return False
    for st in subtriggers:
        truth.append(verifyTrigger(st))
        valid = pre_validate(truth, operator)
        if (valid == True):
            return True
        if (valid == False):
            return False
    return validate(truth, operator)

def gatherServiceInfo(automation):
    services = []
    actions = Graph.getModel().get_targets(automation, DOME.performs)
    for action in actions:
        prop = Graph.getModel().get_target(action, DOME.actuates)
        service = Graph.getModel().get_target(action, DOME.callservice)
        ha_name, ha_type = retrievePropInfo(prop)
        services.append({
            'service': str(service),
            'ha_name': ha_name,
            'ha_type': ha_type
        })
    return services

def retrievePropInfo(prop):
    query_string = """
    PREFIX dome: <http://kadjanderman.com/ontology/>
        SELECT ?ha_name ?ha_type
        {{
            ?device dome:actuates       <{}> ;
                    a                   dome:Device ;
                    dome:ha_name        ?ha_name ;
                    dome:ha_type        ?ha_type .
        }}
    """.format(str(prop))
    q1 = Query(query_string, query_language='sparql')
    results = q1.execute(Graph.getModel())
    for result in results:
        ha_name = str(result['ha_name'])
        ha_type = str(result['ha_type'])
        return (ha_name, ha_type)