from flask import Blueprint, render_template, abort, redirect, url_for, request
from jinja2 import TemplateNotFound

from dome.util.kb import KnowledgeGraph
from dome.config import DOME_NAMESPACE as DOME

bp = Blueprint('init', __name__, url_prefix='/init', template_folder='templates')

@bp.route('/home', methods=('GET', 'POST'))
def home():
    if(request.method == 'POST'):
        homename = request.form['hname']
        graph = KnowledgeGraph()
        home_id = 'home_' + homename
        print('homename: ' + homename)
        print('home_id: ' + home_id)
        graph.add_home(home_id, homename)
        graph.commit()
        del graph
        return redirect(url_for('init.room'))
    try:
        return render_template('init_home.html')
    except TemplateNotFound:
        return abort(404)

@bp.route('/room')
def room():
    graph = KnowledgeGraph()
    test_list = graph.list_by_type(DOME.Device, label=True) + graph.list_by_type(DOME.Property, label=True)
    try:
        return render_template('init_room.html', rooms=test_list)
    except TemplateNotFound:
        return abort(404)