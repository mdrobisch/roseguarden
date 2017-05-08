import os
from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy, orm
from flask_migrate import Migrate
from flask_alchemydumps import AlchemyDumps

from flask_httpauth import HTTPBasicAuth
from flask_mail import Mail
from extension import ExtensionManager
from config import ConfigManager
import datetime

app = Flask(__name__, static_url_path='', static_folder='../extensions/' + ExtensionManager.extension_name + '/frontend')
# have a look at
# http://stackoverflow.com/questions/26722279/how-to-set-static-url-path-in-flask-application
# http://flask.pocoo.org/snippets/102/
flask_bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/roseGuarden.db'
app.config['SQLALCHEMY_MIGRATE_DATABASE_URI'] = 'sqlite:///database/roseGuarden.db'
app.config['WTF_CSRF_ENABLED'] = ConfigManager.WTF_CSRF_ENABLED
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = ConfigManager.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['DEBUG'] = ConfigManager.DEBUG
db = SQLAlchemy(app)

migrate = Migrate(app, db)
alchemydumps = AlchemyDumps(app, db)

api = Api(app)
auth = HTTPBasicAuth()

mail = Mail(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')

    # cahce

    response.headers['Last-Modified'] = datetime.datetime.now()
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response

@app.route('/')
def root():
    return app.send_static_file('index.html')

import views
