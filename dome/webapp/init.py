from flask import Blueprint, render_template, abort, redirect, url_for, request
from jinja2 import TemplateNotFound

from dome.util.kb import KnowledgeGraph
from dome.config import DOME_NAMESPACE as DOME
from rdflib import RDFS, RDF

bp = Blueprint('init', __name__, url_prefix='/init', template_folder='templates')

@bp.route('/home', methods=('GET', 'POST'))
def home():
    if(request.method == 'POST'):
        home_name = request.form['hname']
        
        graph = KnowledgeGraph()
        graph.add_home(home_name)
        graph.commit()
        del graph
        return redirect(url_for('init.room'))
    try:
        return render_template('init_home.html')
    except TemplateNotFound:
        return abort(404)

@bp.route('/room', methods=('GET', 'POST'))
def room():
    graph = KnowledgeGraph()

    if(request.method == 'POST'):
        room_name = request.form['rname']

        graph.add_room(room_name)
        graph.commit()
    
    room_list = graph.get_entities_by_type(DOME.Room, mode=1)
    del graph
    try:
        return render_template('init_room.html', rooms=room_list)
    except TemplateNotFound:
        return abort(404)

@bp.route('/devprop', methods=('GET', 'POST'))
def devprop():
    graph = KnowledgeGraph()

    if (request.method == 'POST'):
        entity_id = request.form['id']
        entity_label = request.form['label']
        graph.modify_literal(entity_id, RDFS.label, entity_label)
        graph.commit()

    device_list = graph.get_entities_by_type(DOME.Device)
    property_list = graph.get_entities_by_type(DOME.Property)
    
    del graph
    try:
        return render_template('init_devprop.html', 
            devices=device_list,
            properties=property_list,
            RDFS_label=str(RDFS.label),
            RDF_type=str(RDF.type),
            DOME_actuates=str(DOME.actuates),
            DOME_observes=str(DOME.observes))
    except TemplateNotFound:
        return abort(404)

@bp.route('/foi', methods=('GET', 'POST'))
def foi():
    graph = KnowledgeGraph()

    if (request.method == 'POST'):
        foi_label = request.form['label']
        foi_location = request.form['location']

        foi_properties = []
        for key in request.form.keys():
            if('prop_' in key):
                foi_properties.append(request.form[key])

        if (request.form['id'] != ""):
            entity_id = request.form['id']
            graph.remove(entity_id, None, None)
        graph.add_foi(foi_label, foi_location, foi_properties)
        graph.commit()
            
    foi_list = graph.get_entities_by_type(DOME.FeatureOfInterest)
    room_list = graph.get_entities_by_type(DOME.Home) + graph.get_entities_by_type(DOME.Room)
    property_list = graph.get_entities_by_type(DOME.Property)

    print('--------- Feature of Interest ---------')
    for f in foi_list:
        print(f)
        print()

    del graph
    try:
        return render_template('init_foi.html', 
            foi_list=foi_list,
            room_list=room_list,
            property_list=property_list,
            RDFS_label=str(RDFS.label),
            DOME_hasprop=str(DOME.hasproperty))
    except TemplateNotFound:
        return abort(404)