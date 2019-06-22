import sys, os
sys.path.append(os.path.abspath(os.path.join('lib', 'redland', 'bindings', 'python')))
from RDF import Uri, Statement

from dome.db.graph import Graph
from dome.config import DOME

if (len(sys.argv) != 2):
    sys.exit()

resource = sys.argv[1]
for stmt in Graph.getModel().find_statements(Statement(Uri(resource), None, None)):
    del Graph.getModel()[stmt]

for stmt in Graph.getModel().find_statements(Statement(None, None, Uri(resource))):
    del Graph.getModel()[stmt]