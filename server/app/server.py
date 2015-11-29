from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, fields, marshal_with
from flask_httpauth import HTTPBasicAuth
from flask_mail import Mail


app = Flask(__name__)

flask_bcrypt = Bcrypt(app)
app.config.from_object('app.config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/roseGuarden.db'
app.config['SQLALCHEMY_MIGRATE_DATABASE_URI'] = 'sqlite:///database/roseGuarden.db'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

api = Api(app)
auth = HTTPBasicAuth()

mail = Mail(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

import views
