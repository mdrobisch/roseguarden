__author__ = 'drobisch'

from server import db, flask_bcrypt
from wtforms.validators import Email
import random
import base64
import datetime
import marshmallow

class User(db.Model):
    ACCESSTYPE_NO_ACCESS = 0
    ACCESSTYPE_ACCESS_PERIOD = 1
    ACCESSTYPE_ACCESS_DAYS = 2
    ACCESSTYPE_LIFETIME_ACCESS = 3
    ACCESSTYPE_MONTHLY_BUDGET = 4
    ACCESSTYPE_QUARTERLY_BUDGET = 5
    ACCESSTYPE_MAX = 6

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
    accessDayCyclicBudget = db.Column(db.Integer)
    lastAccessDaysUpdateDate = db.Column(db.DateTime)
    lastLoginDateTime = db.Column(db.DateTime)
    lastSyncDateTime = db.Column(db.DateTime)
    registerDateTime = db.Column(db.DateTime)
    lastAccessDateTime = db.Column(db.DateTime)
    budget = db.Column(db.Float)
    lastBudgetUpdateDate = db.Column(db.DateTime)

    def checkUserAccessPrivleges(self):
        # check for invalid accessType == no access
        if self.accessType == self.ACCESSTYPE_NO_ACCESS or self.accessType > self.ACCESSTYPE_MAX:
            return 'Denied access because of unauthorized access type.'
        # check start-date and end-date for accessType == period
        if self.accessType == self.ACCESSTYPE_ACCESS_PERIOD:
            if self.accessDateStart > datetime.datetime.now():
                return 'Denied access because of invalid start of period.'
            if self.accessDateEnd < datetime.datetime.now():
                return 'Denied access because of invalid end of period.'
        # check day counter for accessType == day-budget
        if self.accessType == self.ACCESSTYPE_ACCESS_DAYS:
            if self.accessDayCounter <= 0:
                return 'Denied access because of insufficient day-budget.'
        if (int(1 << datetime.datetime.now().weekday()) & self.accessDaysMask) == 0:
            return 'Denied access because of invalid access weekday.'
        if self.accessTimeStart.time() > datetime.datetime.now().time():
            return 'Denied access because of invalid day-time start.'
        if self.accessTimeEnd.time() < datetime.datetime.now().time():
            return 'Denied access because of invalid day-time end.'
        return "Access granted."


    def updateUserFromSyncDict(self, data):
        self.syncMaster = data['syncMaster']
        self.active = data['active']
        self.phone = data['phone']
        self.cardAuthBlock = data['cardAuthBlock']
        self.cardAuthSector = data['cardAuthSector']
        self.cardID = data['cardID']
        self.cardSecret = data['cardSecret']
        self.cardAuthKeyA = data['cardAuthKeyA']
        self.cardAuthKeyB = data['cardAuthKeyB']
        self.role = data['role']
        self.email = data['email']
        self.password = data['password']
        self.firstName = data['firstName']
        self.lastName = data['lastName']
        self.association = data['association']
        self.phone = data['phone']
        self.keyMask = data['keyMask']
        self.licenseMask = data['licenseMask']
        self.accessDaysMask = data['accessDaysMask']
        self.accessType = data['accessType']
        self.accessDayCounter = data['accessDayCounter']
        self.accessDayCyclicBudget = data['accessDayCyclicBudget']

        if self.lastLoginDateTime < datetime.datetime.strptime(data['lastLoginDateTime'][:19], '%Y-%m-%dT%H:%M:%S'):
            self.lastLoginDateTime = datetime.datetime.strptime(data['lastLoginDateTime'][:19], '%Y-%m-%dT%H:%M:%S')
        if self.lastAccessDateTime < datetime.datetime.strptime(data['lastLoginDateTime'][:19], '%Y-%m-%dT%H:%M:%S'):
            self.lastAccessDateTime = datetime.datetime.strptime(data['lastLoginDateTime'][:19], '%Y-%m-%dT%H:%M:%S')
        if self.lastBudgetUpdateDate < datetime.datetime.strptime(data['lastBudgetUpdateDate'][:19], '%Y-%m-%dT%H:%M:%S'):
            self.lastBudgetUpdateDate = datetime.datetime.strptime(data['lastBudgetUpdateDate'][:19], '%Y-%m-%dT%H:%M:%S')

        self.lastAccessDaysUpdateDate = datetime.datetime.strptime(data['lastAccessDaysUpdateDate'][:19], '%Y-%m-%dT%H:%M:%S')
        self.registerDateTime = datetime.datetime.strptime(data['registerDateTime'][:19], '%Y-%m-%dT%H:%M:%S')
        self.accessDateStart = datetime.datetime.strptime(data['accessDateStart'][:19], '%Y-%m-%dT%H:%M:%S')
        self.accessDateEnd = datetime.datetime.strptime(data['accessDateEnd'][:19], '%Y-%m-%dT%H:%M:%S')
        self.accessTimeStart = datetime.datetime.strptime(data['accessTimeStart'][:19], '%Y-%m-%dT%H:%M:%S')
        self.accessTimeEnd = datetime.datetime.strptime(data['accessTimeEnd'][:19], '%Y-%m-%dT%H:%M:%S')
        self.accessTimeEnd = datetime.datetime.strptime(data['accessTimeEnd'][:19], '%Y-%m-%dT%H:%M:%S')

        self.budget = data['budget']

    def __repr__(self):
        return '<User %r>' % self.email

    def __init__(self, email, password, firstName, lastName, role = 0, phone='0', licenseMask =0, keyMask = 0, association = ''):
        self.syncMaster = 0
        self.active = 1
        self.phone = phone
        self.cardAuthBlock = 1
        self.cardAuthSector = 4
        self.cardID = ''
        self.cardSecret = ''
        self.cardAuthKeyA = ''
        self.cardAuthKeyB = ''
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
        self.accessDayCounter = 10
        self.accessDayCyclicBudget = 10
        self.lastAccessDaysUpdateDate = (datetime.datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)
        self.accessDateStart = (datetime.datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)
        self.accessDateEnd = (datetime.datetime.today() + datetime.timedelta(365*15)).replace(hour=0,minute=0,second=0,microsecond=0)
        self.accessTimeStart = datetime.datetime.today().replace(hour= 0, minute= 1, second=0, microsecond=0)
        self.accessTimeEnd = datetime.datetime.today().replace(hour= 23, minute= 59, second=0, microsecond=0)
        self.lastAccessDateTime = (datetime.datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)
        self.lastLoginDateTime = datetime.datetime.today()
        self.lastSyncDateTime = datetime.datetime.now()
        self.registerDateTime = datetime.datetime.today()
        self.budget = 0.00;
        self.lastBudgetUpdateDate = (datetime.datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)

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

class Action(db.Model):
    ACTION_LOGONLY = 0
    ACTION_OPENING_REQUEST = 1

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
    action = db.Column(db.Integer)
    actionParameter = db.Column(db.Integer)
    rollbackPoint = db.Column(db.Integer)
    synced = db.Column(db.Integer)

    def __init__(self, date, nodeName, userName, userMail, logText, logType, logLevel, authType, authInfo, action = ACTION_LOGONLY, actionParameter = 0, rollbackpoint = -1):
        self.date = date
        self.nodeName = nodeName
        self.userName = userName
        self.userMail = userMail
        self.logType = logType
        self.logLevel = logLevel
        self.logText = logText
        self.authType = authType
        self.authInfo = authInfo
        self.synced = 0
        self.action = action
        self.actionParameter = actionParameter
        self.rollbackPoint = rollbackpoint

class Door(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    displayName = db.Column(db.Text)
    keyMask = db.Column(db.Integer)
    address = db.Column(db.Text)
    local = db.Column(db.Integer)
    password = db.Column(db.Text)

    def __init__(self, name, displayName, keyMask, address, local, password = ''):
        self.name = name
        self.displayName = displayName
        self.keyMask = keyMask
        self.address = address
        self.local = local
        self.password = base64.b64encode(password)

class RfidTagInfo(object):
    def __init__(self, tagId, userInfo):
        self.userInfo = userInfo
        self.tagId = tagId
