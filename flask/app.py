from kb import KnowledgeGraph
import config
DOME = config.DOME_NAMESPACE

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
@app.route('/<t>')
def list_entities(t='property'):
    g = KnowledgeGraph()
    entity_list = []
    if(t == 'property'):
        entity_type = DOME.Property
    elif(t == 'device'):
        entity_type = DOME.Device
    else:
        return render_template('index.html', entity_list=[])
    entity_list = g.list_by_type(entity_type)
    return render_template('index.html', entity_list=entity_list)
    
    