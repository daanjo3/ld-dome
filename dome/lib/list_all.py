import sys
import sys, os
sys.path.append(os.path.abspath(os.path.join('lib', 'redland', 'bindings', 'python')))

from dome.db.graph import Graph

for statement in Graph.getModel():
    print(statement)