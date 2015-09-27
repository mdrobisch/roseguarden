__author__ = 'drobisch'

from server import db, flask_bcrypt
from wtforms.validators import Email
import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False, info={'validators': Email()})
    password = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text)
    tokenExpirationDate = db.Column(db.DateTime)
    firstName = db.Column(db.Text)
    lastName = db.Column(db.Text)
    phone = db.Column(db.Text)
    role = db.Column(db.Integer)
    cardID = db.Column(db.Text)
    cardPassword = db.Column(db.Text)
    license = db.Column(db.Integer)
    key = db.Column(db.Integer)
    accessType = db.Column(db.Integer)
    accessDateStart = db.Column(db.DateTime)
    accessDateEnd = db.Column(db.DateTime)
    accessTimeStart = db.Column(db.DateTime)
    accessTimeEnd = db.Column(db.DateTime)
    accessDays = db.Column(db.Integer)
    accessDayCounter = db.Column(db.Integer)
    lastLoginDateTime = db.Column(db.DateTime)
    registerDateTime = db.Column(db.DateTime)
    budget = db.Column(db.Float)

    def __repr__(self):
        return '<User %r>' % self.email
    def __init__(self, email, password, firstName, lastName, role = 0,phone = '0',license = 0, key = 0):
        self.phone = phone
        self.role = role;
        self.email = email
        self.password = flask_bcrypt.generate_password_hash(password)
        self.firstName = firstName
        self.lastName = lastName
        self.phone = phone
        self.key = key
        self.license = license
        self.accessDays = 127
        self.accessType = 0
        self.accessDateStart = (datetime.datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)
        self.accessDateEnd = (datetime.datetime.today() + datetime.timedelta(365*15)).replace(hour=0,minute=0,second=0,microsecond=0)
        self.accessTimeStart = datetime.datetime.today().replace(hour= 6, minute= 0, second=0, microsecond=0)
        self.accessTimeEnd = datetime.datetime.today().replace(hour= 22, minute= 30, second=0, microsecond=0)
        self.lastLoginDateTime = datetime.datetime.today()
        self.registerDateTime = datetime.datetime.today()
        self.budget = 0.00;


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    value = db.Column(db.Text)
    type = db.Column(db.Integer)
    def __init__(self, name,value,type):
        self.name = name
        self.type = type
        self.value = value

class Door(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    keyMask = db.Column(db.Integer)
    address = db.Column(db.Text)
    local = db.Column(db.Integer)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.Text, nullable=False)
    userMail = db.Column(db.Text, nullable=False, info={'validators': Email()})
    cardID = db.Column(db.Text)
    requestName = db.Column(db.Text)
    requestType = db.Column(db.Text)
    date = db.Column(db.Date)
    def __init__(self, userName, userMail, cardID, requestName,requestType, date = datetime.datetime.now()):
        self.userName = userName
        self.userMail = userMail
        self.requestName = requestName
        self.requestType = requestType
        self.cardID = cardID
        self.date = date
