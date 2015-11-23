__author__ = 'drobisch'

from server import db, flask_bcrypt
from wtforms.validators import Email
import random
import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    syncMaster = db.Column(db.Integer)
    active = db.Column(db.Integer)
    email = db.Column(db.Text, unique=True, nullable=False, info={'validators': Email()})
    password = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text)
    tokenExpirationDate = db.Column(db.DateTime)
    firstName = db.Column(db.Text)
    lastName = db.Column(db.Text)
    phone = db.Column(db.Text)
    association = db.Column(db.Text)
    role = db.Column(db.Integer)
    cardID = db.Column(db.Text)
    cardAuthSector = db.Column(db.Integer)
    cardAuthBlock = db.Column(db.Integer)
    cardAuthKeyA = db.Column(db.Text)
    cardAuthKeyB = db.Column(db.Text)
    cardSecret = db.Column(db.Text)
    licenseMask = db.Column(db.Integer)
    keyMask = db.Column(db.Integer)
    accessType = db.Column(db.Integer)
    accessDateStart = db.Column(db.DateTime)
    accessDateEnd = db.Column(db.DateTime)
    accessTimeStart = db.Column(db.DateTime)
    accessTimeEnd = db.Column(db.DateTime)
    accessDaysMask = db.Column(db.Integer)
    accessDayCounter = db.Column(db.Integer)
    lastLoginDateTime = db.Column(db.DateTime)
    registerDateTime = db.Column(db.DateTime)
    budget = db.Column(db.Float)

    def checkUserAccessPrivleges(self):
        # check for invalid accessType == no access
        if self.accessType == 0 or self.accessType > 3:
            return 'invalid access because of access type'
        # check start-date and end-date for accessType == period
        if self.accessType == 1:
            if self.accessDateStart > datetime.datetime.now():
                return 'invalid access because of DateStart'
            if self.accessDateEnd < datetime.datetime.now():
                return 'invalid access because of DateEnd'
        # check day counter for accessType == day-budget
        if self.accessType == 2:
            if self.accessDayCounter <= 0:
                return 'invalid access because of day-counter'
        if (int(1 << datetime.datetime.now().weekday()) & self.accessDaysMask) == 0:
            return 'invalid access because of access weekdays'
        if self.accessTimeStart.time() > datetime.datetime.now().time():
            return 'invalid access because of TimeStart'
        if self.accessTimeEnd.time() < datetime.datetime.now().time():
            return 'invalid access because of TimeEnd'
        return "access granted"

    def __repr__(self):
        return '<User %r>' % self.email

    def __init__(self, email, password, firstName, lastName, role = 0, phone='0', licenseMask =0, keyMask = 0, association = ''):
        self.syncMaster = 0
        self.active = 1
        self.phone = phone
        self.cardAuthBlock = 1
        self.cardAuthSector = 4
        self.cardID = ''
        self.cardKey = ''
        self.cardSecret = ''
        self.cardAuthKeyA = 'FF FF FF FF FF FF'
        self.cardAuthKeyB = ''
        self.cardSecret = ''

        self.role = role;
        self.email = email
        self.password = flask_bcrypt.generate_password_hash(password)
        self.firstName = firstName
        self.lastName = lastName
        self.association = association
        self.phone = phone
        self.keyMask = keyMask
        self.licenseMask = licenseMask
        self.accessDaysMask = 127
        self.accessType = 0
        self.accessDayCounter = 0
        self.accessDateStart = (datetime.datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)
        self.accessDateEnd = (datetime.datetime.today() + datetime.timedelta(365*15)).replace(hour=0,minute=0,second=0,microsecond=0)
        self.accessTimeStart = datetime.datetime.today().replace(hour= 6, minute= 0, second=0, microsecond=0)
        self.accessTimeEnd = datetime.datetime.today().replace(hour= 22, minute= 30, second=0, microsecond=0)
        self.lastLoginDateTime = datetime.datetime.today()
        self.registerDateTime = datetime.datetime.today()
        self.budget = 0.00;


class Setting(db.Model):
    WRITEONLY = 0x80
    WRITEONLY = 0x40
    VALUETYPE_STRING = 1
    VALUETYPE_INT = 1
    VALUETYPE_FLOAT = 1

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    value = db.Column(db.Text)
    type = db.Column(db.Integer)

    def __init__(self, name,value,type):
        self.name = name
        self.type = type
        self.value = value

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    nodeName = db.Column(db.Text)
    userName = db.Column(db.Text)
    userMail = db.Column(db.Text)
    authType = db.Column(db.Integer)
    authInfo = db.Column(db.Text)
    logText = db.Column(db.Text)
    logType = db.Column(db.Text)
    logLevel = db.Column(db.Text)

    def __init__(self, date, nodeName, userName, userMail, logText, logType, logLevel, authType, authInfo):
        self.date = date
        self.nodeName = nodeName
        self.userName = userName
        self.userMail = userMail
        self.logType = logType
        self.logLevel = logLevel
        self.logText = logText
        self.authType = authType
        self.authInfo = authInfo

class Door(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    keyMask = db.Column(db.Integer)
    address = db.Column(db.Text)
    local = db.Column(db.Integer)

    def __init__(self, name,keyMask,address,local):
        self.name = name
        self.keyMask = keyMask
        self.address = address
        self.local = local

class RfidTagInfo(object):
    def __init__(self, tagId, userInfo):
        self.userInfo = userInfo
        self.tagId = tagId
