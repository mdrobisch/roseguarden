__author__ = 'drobisch'

from server import db, orm
from wtforms.validators import Email
from werkzeug.security import generate_password_hash, check_password_hash
import random
import base64
import datetime
import marshmallow

class User(db.Model):
    ACCESSTYPE_NO_ACCESS = 0
    ACCESSTYPE_DAILY_ACCESS_PERIOD = 1
    ACCESSTYPE_ACCESS_DAYS = 2
    ACCESSTYPE_LIFETIME_ACCESS = 3
    ACCESSTYPE_MONTHLY_BUDGET = 4
    ACCESSTYPE_QUARTERLY_BUDGET = 5
    ACCESSTYPE_ABSOLUT_ACCESS_PERIOD = 6
    ACCESSTYPE_MAX = 7

    AUTHTYPE_WEB    = 0
    AUTHTYPE_RFID   = 1

    ROLE_USER           = 0
    ROLE_ADMIN          = 1
    ROLE_SUPERVISOR     = 2

    MONDAY          = 1
    TUESDAY         = 2
    WEDNESDAY       = 4
    THURSDAY        = 8
    FRIDAY          = 16
    SATURDAY        = 32
    SUNDAY          = 64

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
    weeklyAccessAverage = db.Column(db.Integer)
    weeklyAccessWeekNumber = db.Column(db.Integer)
    weeklyAccessCount = db.Column(db.Integer)
    monthlyAccessAverage = db.Column(db.Integer)
    monthlyAccessMonthNumber = db.Column(db.Integer)
    monthlyAccessCount = db.Column(db.Integer)
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

    @orm.reconstructor
    def init_on_load(self):
        if self.cardID == "":
            self.cardIDAssigned = 0
        else:
            self.cardIDAssigned = 1

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
        self.role = role
        self.email = email.lower()
        self.password = generate_password_hash(unicode(password))
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
        self.weeklyAccessAverage = 0
        self.weeklyAccessWeekNumber = datetime.datetime.now().isocalendar()[1]
        self.weeklyAccessCount = 0
        self.monthlyAccessAverage = 0
        self.monthlyAccessMonthNumber = datetime.datetime.now().month
        self.monthlyAccessCount = 0
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
    WRITEABLE = 0x100
    SETTINGTYPE_STRING  = 1
    SETTINGTYPE_INT     = 2
    SETTINGTYPE_FLOAT   = 3
    SETTINGTYPE_BOOL    = 4

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

class StatisticEntry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    statId = db.Column(db.Integer)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    binningId = db.Column(db.Integer)
    series = db.Column(db.Integer)
    label = db.Column(db.Text)
    value = db.Column(db.Float)

    def __init__(self, statId, label, value, series, month, year, binningId):
        self.statId = statId
        self.label = label
        self.value = value
        self.series = series
        self.month = month
        self.year = year
        self.binningId = binningId


class Statistic(db.Model):
    STATTYPE_LINE_SERIES = 1
    STATTYPE_BAR_SERIES = 2
    STATTYPE_RADAR_SERIES = 3
    STATTYPE_DOUGHNUT_CLASSES = 5
    STATTYPE_RADAR_CLASSES = 6
    STATTYPE_YEARLY_BAR_SERIES = 8

    STATDISPLAY_CONFIG_SHOW_DESCRIPTION = 1
    STATDISPLAY_CONFIG_NO_TOTAL = 2

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    displayConfig = db.Column(db.Integer)
    description = db.Column(db.Text)
    statId = db.Column(db.Integer)
    statType = db.Column(db.Integer)
    binningCount = db.Column(db.Integer)
    seriesCount = db.Column(db.Integer)
    seriesName1 = db.Column(db.Text)
    seriesName2 = db.Column(db.Text)
    seriesName3 = db.Column(db.Text)
    seriesName4 = db.Column(db.Text)
    seriesName5 = db.Column(db.Text)
    seriesName6 = db.Column(db.Text)
    seriesName7 = db.Column(db.Text)
    seriesName8 = db.Column(db.Text)

    def __init__(self, name, statId, statType, binningCount = 0, seriesCount = 0, description = '', displayConfig = 0, seriesName1 = '', seriesName2 = '', seriesName3 = '', seriesName4 = '', seriesName5 = '', seriesName6 = '', seriesName7 = '', seriesName8 = ''):
        self.name = name
        self.displayConfig = displayConfig
        self.description = description
        self.statId = statId
        self.statType = statType
        self.binningCount = binningCount
        self.seriesCount = seriesCount
        self.seriesName1 = seriesName1
        self.seriesName2 = seriesName2
        self.seriesName3 = seriesName3
        self.seriesName4 = seriesName4
        self.seriesName5 = seriesName5
        self.seriesName6 = seriesName6
        self.seriesName7 = seriesName7
        self.seriesName8 = seriesName8

class NodeLink(db.Model):
    NODETYPE_MASTER = 0
    NODETYPE_DOOR = 1

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    displayName = db.Column(db.Text)
    keyMask = db.Column(db.Integer)
    address = db.Column(db.Text)
    local = db.Column(db.Integer)
    type = db.Column(db.Integer)
    password = db.Column(db.Text)

    def __init__(self, name, displayName, keyMask, address, local, password = '', type=NODETYPE_DOOR):
        self.name = name
        self.displayName = displayName
        self.keyMask = keyMask
        self.address = address
        self.local = local
        self.password = base64.b64encode(password)
        self.type = type

class RfidTagInfo(object):
    def __init__(self, tagId, userInfo, detected=False,error=False, errorInfo=''):
        self.userInfo = userInfo
        self.detected = detected
        self.tagId = tagId
        self.error = error
        self.errorInfo = errorInfo
