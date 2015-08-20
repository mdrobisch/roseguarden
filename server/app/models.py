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
    validKeyTimeStart = db.Column(db.DateTime)
    validKeyTimeEnd = db.Column(db.DateTime)
    validKeyPeriodStart = db.Column(db.DateTime)
    validKeyPeriodEnd = db.Column(db.DateTime)
    validKeyDays = db.Column(db.Integer)
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
        self.licenseM = license

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
