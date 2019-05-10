from flask import Blueprint, render_template, abort, redirect, url_for, request
from jinja2 import TemplateNotFound

from dome.util.kb import KnowledgeGraph
from dome.config import DOME_NAMESPACE as DOME

bp = Blueprint('init', __name__, url_prefix='/init', template_folder='templates')

@bp.route('/home', methods=('GET', 'POST'))
def home():
    if(request.method == 'POST'):
        home_name = request.form['hname']
        home_id = 'home_' + home_name
        
        graph = KnowledgeGraph()
        graph.add_home(home_id, home_name)
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
        room_id = 'room_' + room_name

        graph.add_room(room_id, room_name)
        graph.commit()
    
    room_list = graph.list_by_type(DOME.Room, label=True)
    del graph
    try:
        return render_template('init_room.html', rooms=room_list)
    except TemplateNotFound:
        return abort(404)

@bp.route('/devprop')
def devprop():
    try:
        return render_template('init_dev_prop.html')
    except TemplateNotFound:
        return abort(404)