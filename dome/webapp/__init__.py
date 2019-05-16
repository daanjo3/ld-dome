from flask import Flask, render_template, request
app = Flask(__name__)

# import dome.webapp.views
@app.route('/', methods=('GET', 'POST'))
def index():
    if(request.method == 'POST'):
        home_name = request.form['hname']
    return render_template('index.html')

from . import init
app.register_blueprint(init.bp)