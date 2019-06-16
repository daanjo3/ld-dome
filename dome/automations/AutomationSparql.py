import sys, os
sys.path.append(os.path.abspath(os.path.join('lib', 'redland', 'bindings', 'python')))

from RDF import Query, Uri
from dome.db.graph import Graph

def getWatchlist():
    q_watchlist = Query("""
        PREFIX dome: <http://kadjanderman.com/ontology/>
        SELECT ?property WHERE
        {
            ?condition a dome:Condition .
            ?condition dome:observes ?property .
        }""", query_language="sparql")
    
    results = q_watchlist.execute(Graph.getModel())
    watchlist = []
    for result in results:
        prop_src = Uri(str(result['property']))
        if (prop_src not in watchlist):
            watchlist.append(prop_src)
    return watchlist

def getWatchlist():
    main_trigger = Graph.getModel().get_target()

def getActiveCondition(prop_src):
    q_watchlist = Query(("""
        PREFIX dome:<"http://kadjanderman.com/ontology/>
        SELECT ?condition WHERE
        {
            ?condition a dome:Condition .
            ?condition dome:observes {}
        }
    """.format(prop_src)), query_language="sparql")

    results = q_watchlist.execute(Graph.getModel())
    conditions = []
    for result in results:
        cond_src = Uri(str(results['property']))
        if (cond_src not in conditions):
            conditions.append(cond_src)
    
        

if __name__ == "__main__":
    print([str(res) for res in get_watchlist()])