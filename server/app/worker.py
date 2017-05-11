import requests

__author__ = 'drobisch'

import flask_alchemydumps
import threading
import time
import base64
import json
import datetime
import helpers
import security
import os

from config import ConfigManager
from extension import ExtensionManager
from models import User, NodeLink, Action
from server import app, db
from serializers import LogSerializer, UserSyncSerializer
from statistics import StatisticsManager
from dateutil.relativedelta import relativedelta
from models import RfidTagInfo
from drivers.authentication.RFID import RFIDReader
from drivers.common.GPIO import GPIO

GPIO_RELAY = 12
GPIO_LED_GREEN = 11
GPIO_LED_YELLOW = 13
GPIO_LED_RED = 15

class BackgroundWorker():

    def __init__(self, app):
        # initialize worker variables
        self.LED_STATE_IDLE = 0
        self.LED_STATE_ACCESS_GRANTED = 1
        self.LED_STATE_ACCESS_DENIED = 2
        self.LED_STATE_CLOSED = 3


        self.first = True
        self.app = app
        self.requestOpening = False
        self.openingTimer = -1
        self.requestTimer = 0
        self.syncTimer = 0
        self.ledStateTimer = 0
        self.ledState = self.LED_STATE_IDLE
        self.ledStateCounter = 0

        self.systemUp = True
        if ConfigManager.NODE_SYNC_ON_STARTUP is True:
            self.forceSync = True
        else:
            self.forceSync = False
        self.forceBackup = False
        self.backupTimer = 0
        self.cleanupTimer = 0
        self.tagInfo = RfidTagInfo("", "")
        self.tagResetCount = 0
        self.lock = False
        self.lastBackupTime = datetime.datetime.now()
        self.lastCleanupTime = datetime.datetime.now().replace(1910)
        self.lastSyncTime = datetime.datetime.now()

        # setup gpio and set default (Low)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIO_RELAY, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.output(GPIO_RELAY, GPIO.HIGH)

        GPIO.setup(GPIO_LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(GPIO_LED_GREEN, GPIO.LOW)

        GPIO.setup(GPIO_LED_YELLOW, GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(GPIO_LED_YELLOW, GPIO.LOW)

        GPIO.setup(GPIO_LED_RED, GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(GPIO_LED_RED, GPIO.LOW)



    def run(self):
        # if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        self.thr = threading.Timer(1, self.timer_cycle)

        if(ExtensionManager.extension.CONFIG_DISABLE_UPDATE_USER is False):
            self.update_users_and_actions()

        self.thr.start()
        print 'started background-server ' + '(' + str(datetime.datetime.now()) + ')'

    def resetTagInfo(self):
        self.tagInfo.tagId = ""
        self.tagInfo.userInfo = ""
        self.tagInfo.detected = False
        self.tagInfo.error = False
        self.tagInfo.errorInfo = ""

    def withdrawRFIDTag(self, user):
        while (self.lock == True):
            if ConfigManager.DEBUG == False:
                print "still locked (withdrawRFIDTag)"
            time.sleep(0.3)

        try:
            self.lock = True

            time.sleep(0.2)

            print "background-worker withdrawRFIDTag"

            for i in range(0, 4):
                (status, TagType) = RFIDReader.MFRC522_Request(RFIDReader.PICC_REQIDL)
                (status, uid) = RFIDReader.MFRC522_Anticoll()
                if status == RFIDReader.MI_OK:
                    break
                else:
                    print "retry anticoll card (withdrawRFIDTag)"
                    time.sleep(0.3)

            # If we have the UID, continue
            if status == RFIDReader.MI_OK:
                # Print UID
                uid_str = str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3])
                print "Card read UID: " + uid_str

                if (uid_str != user.cardID):
                    print "Wrong cardID detected while withdrawing RFID-tag to user"
                    self.lock = False
                    return False

                # This is the default key for authentication
                defaultkey = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                defaultsecret = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                                 0xFF, 0xFF]

                userkey = []
                usersecret = []

                userkeyString = user.cardAuthKeyA
                for x in userkeyString.split('-'):
                    userkey.append(int(x, 16))

                print "Userkey: " + str(userkey)

                usersecretString = user.cardSecret
                for x in usersecretString.split('-'):
                    usersecret.append(int(x, 16))

                print "Usersecret: " + str(usersecret)

                SecretBlockAddr = user.cardAuthSector * 4 + user.cardAuthBlock
                TrailerBlockAddr = user.cardAuthSector * 4 + 3

                # Select the scanned tag
                RFIDReader.MFRC522_SelectTag(uid)

                # Authenticate for secret-block
                status = RFIDReader.MFRC522_Auth(RFIDReader.PICC_AUTHENT1A, SecretBlockAddr, userkey, uid)

                # write user secret
                if status == RFIDReader.MI_OK:
                    RFIDReader.MFRC522_Write(SecretBlockAddr, defaultsecret)
                else:
                    print "Authentication error while write rfid-tag secret sector"
                    self.lock = False
                    return False

                status = RFIDReader.MFRC522_Auth(RFIDReader.PICC_AUTHENT1A, TrailerBlockAddr, userkey, uid)

                # Check if authenticated
                if status == RFIDReader.MI_OK:
                    print "Read TrailerBlock :"
                    # Read block 8
                    result = RFIDReader.MFRC522_Read(TrailerBlockAddr)
                    print result

                    for x in range(0, 6):
                        result[x] = 0xFF
                    print result

                    print "Write new trailer:"
                    # Write the data
                    RFIDReader.MFRC522_Write(TrailerBlockAddr, result)
                    print "\n"

                    RFIDReader.MFRC522_StopCrypto1()
                    # unlock and return succesfully
                    self.lock = False
                    return True
                else:
                    print "Authentication error while write rfid-tag key sector"
                    self.lock = False
                    return False
            else:
                print "Authentication error while looking for cards"
                self.lock = False
                return False
        except:
            self.lock = False
            print "unexpected error withdrawRFIDTag"
            raise

    def assignRFIDTag(self, user):
        while (self.lock == True):
            print "still locked (assignRFIDTag)"
            time.sleep(0.3)
        try:
            # lock the access of the spi-access for the rfid
            self.lock = True

            time.sleep(0.2)

            print "background-worker assignRFIDTag"

            for i in range(0, 4):
                (status, TagType) = RFIDReader.MFRC522_Request(RFIDReader.PICC_REQIDL)
                (status, uid) = RFIDReader.MFRC522_Anticoll()
                if status == RFIDReader.MI_OK:
                    break
                else:
                    print "retry anticoll card (assignRFIDTag)"
                    time.sleep(0.3)

            # If we have the UID, continue
            if status == RFIDReader.MI_OK:
                # Print UID
                uid_str = str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3])
                print "Card read UID: " + uid_str

                if (uid_str != user.cardID):
                    print "Wrong cardID detected while assigning RFID-tag to user"
                    self.lock = False
                    return False

                # This is the default key for authentication
                defaultkey = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                userkey = []
                usersecret = []

                print "Card auth key A:" + str(user.cardAuthKeyA)
                print "Card auth key B:" + str(user.cardAuthKeyB)

                userkeyString = user.cardAuthKeyA
                for x in userkeyString.split('-'):
                    userkey.append(int(x, 16))

                print "Userkey: " + str(userkey)

                usersecretString = user.cardSecret
                for x in usersecretString.split('-'):
                    usersecret.append(int(x, 16))

                print "Usersecret: " + str(usersecret)

                SecretBlockAddr = user.cardAuthSector * 4 + user.cardAuthBlock
                TrailerBlockAddr = user.cardAuthSector * 4 + 3

                # Select the scanned tag
                RFIDReader.MFRC522_SelectTag(uid)

                # Authenticate for secret-block
                status = RFIDReader.MFRC522_Auth(RFIDReader.PICC_AUTHENT1A, SecretBlockAddr, defaultkey, uid)

                # write user secret
                if status == RFIDReader.MI_OK:
                    RFIDReader.MFRC522_Write(SecretBlockAddr, usersecret)
                else:
                    print "Authentication error while write rfid-tag secret sector"
                    self.lock = False
                    return False

                # Authenticate
                status = RFIDReader.MFRC522_Auth(RFIDReader.PICC_AUTHENT1A, TrailerBlockAddr, defaultkey, uid)
                if status == RFIDReader.MI_OK:
                    result = RFIDReader.MFRC522_Read(TrailerBlockAddr)
                    print result

                    for x in range(0, 6):
                        result[x] = userkey[x]
                    print result

                    print "Write new trailer:"
                    # Write the data
                    RFIDReader.MFRC522_Write(TrailerBlockAddr, result)
                    print "\n"

                    RFIDReader.MFRC522_StopCrypto1()
                    # unlock and return succesfully
                    self.lock = False
                    return True
                else:
                    print "Authentication error while write rfid-tag key sector"
                    self.lock = False
                    return False
            else:
                print "Authentication error while looking for cards"
                self.lock = False
                return False
        except:
            self.lock = False
            print "unexpected error assignRFIDTag"
            raise

    def checkRFIDTag(self):

        #if self.first == True:
        #    self.first = False
        #    raise ValueError('A very specific bad thing happened')

        while (self.lock == True):
            print "still locked (checkRFIDTag)"
            time.sleep(0.2)

        try:
            self.lock = True

            (status, TagType) = RFIDReader.MFRC522_Request(RFIDReader.PICC_REQIDL)

            for i in range(0, 2):
                (status, uid) = RFIDReader.MFRC522_Anticoll()
                if status == RFIDReader.MI_OK:
                    break
                else:
                    time.sleep(0.2)

            self.resetTagInfo()

            # If we have the UID, continue
            if status == RFIDReader.MI_OK:

                # Print UID
                self.tagInfo.detected = True
                self.tagInfo.tagId = str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3])
                self.tagInfo.userInfo = ""

                user = User.query.filter_by(cardID=self.tagInfo.tagId).first()

                if user is None:
                    self.ledState = self.LED_STATE_ACCESS_DENIED
                    self.lock = False
                    return

                self.tagInfo.userInfo = user.email
                # print user.email

                # This is the default key for authentication
                defaultkey = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                userkey = []
                usersecret = []

                userkeyString = user.cardAuthKeyA
                for x in userkeyString.split('-'):
                    userkey.append(int(x, 16))

                # print "Userkey: " + str(userkey)

                usersecretString = user.cardSecret
                for x in usersecretString.split('-'):
                    usersecret.append(int(x, 16))

                # print "Usersecret: " + str(usersecret)

                SecretBlockAddr = user.cardAuthSector * 4 + user.cardAuthBlock
                TrailerBlockAddr = user.cardAuthSector * 4 + 3

                # Select the scanned tag
                RFIDReader.MFRC522_SelectTag(uid)

                # Authenticate
                status = RFIDReader.MFRC522_Auth(RFIDReader.PICC_AUTHENT1A, SecretBlockAddr, userkey, uid)

                # Check if authenticated
                if status == RFIDReader.MI_OK:

                    readSecret = RFIDReader.MFRC522_Read(SecretBlockAddr)
                    # print readSecret
                    readSecretString = ''
                    i = 0

                    if not readSecret:
                        print "Read secret string is empty."
                        self.lock = False
                        RFIDReader.MFRC522_StopCrypto1()
                        return False

                    for x in readSecret:
                        if i != 0:
                            readSecretString = readSecretString + '-'
                        i = i + 1
                        readSecretString = readSecretString + format(x, '02X')

                    # print readSecretString

                    if readSecretString == user.cardSecret:
                        print "correct secret"
                        if security.checkUserAccessPrivleges(datetime.datetime.now(),user) == "Access granted.":
                            if datetime.datetime.now() > user.lastAccessDateTime + datetime.timedelta(minutes=ConfigManager.NODE_LOG_MERGE):
                                user.lastAccessDateTime = datetime.datetime.now()

                                logentry = Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, user.firstName + ' ' + user.lastName,
                                               user.email, 'Opening request (' + str(1) + ' attempts)', 'Opening request',
                                               'L2', 1, 'Card based', Action.ACTION_OPENING_REQUEST, 1)
                                print "Log-entry created"
                                try:
                                    db.session.add(logentry)
                                    db.session.commit()
                                except:
                                    self.ledState = self.LED_STATE_ACCESS_DENIED
                                    db.session.rollback()
                                    raise

                            else:
                                lastlogEntry = Action.query.filter_by(logType='Opening request', userMail=user.email).order_by(Action.date.desc()).first()
                                if lastlogEntry is not None:
                                    if lastlogEntry.synced is 0:
                                        lastlogEntry.date = datetime.datetime.utcnow()
                                        lastlogEntry.actionParameter += 1
                                        lastlogEntry.logText = 'Opening request (' + str(lastlogEntry.actionParameter) + ' attempts)'
                                    else:
                                        lastlogEntry.synced = 0
                                        lastlogEntry.date = datetime.datetime.utcnow()
                                        lastlogEntry.actionParameter = 1
                                        lastlogEntry.logText = 'Opening request (' + str(lastlogEntry.actionParameter) + ' attempts)'
                                print "Log-entry is in merge-range ts = " + str(datetime.datetime.now()) + " last = " + str(user.lastAccessDateTime) + " merge = " + str(ConfigManager.NODE_LOG_MERGE) + " minutes"
                                try:
                                    db.session.commit()
                                except:
                                    self.ledState = self.LED_STATE_ACCESS_DENIED
                                    db.session.rollback()
                                    raise

                            self.requestOpening = True
                            self.ledState = self.LED_STATE_ACCESS_GRANTED
                        else:
                            self.ledState = self.LED_STATE_ACCESS_DENIED
                            print "no user-access privilege"
                    else:
                        self.tagInfo.userInfo = user.email + '(inv. sec.)'
                        print "no user-access privilege"
                        self.ledState = self.LED_STATE_ACCESS_DENIED

                    RFIDReader.MFRC522_StopCrypto1()
                    self.lock = False
                    return True
                else:
                    self.tagInfo.userInfo = user.email + '(inv. key.)'
                    print "Authentication error"
                    self.ledState = self.LED_STATE_ACCESS_DENIED
                    self.lock = False
                    return False
            else:
                self.lock = False
                return False
        except:
            self.lock = False
            print "unexpected error in checkRFIDTag"
            self.ledState = self.LED_STATE_ACCESS_DENIED
            raise



    def cleanup_cycle(self):
        lasttime = self.lastCleanupTime
        now = datetime.datetime.now()
        past = now - datetime.timedelta(days=ConfigManager.CLEANUP_THRESHOLD)

        compare_time = lasttime.replace(hour=04, minute=55, second=0, microsecond=0)
        if compare_time > lasttime:
            next_time = compare_time
        else:
            next_time = compare_time + datetime.timedelta(days=1)

        if(now > next_time):
            print 'Doing a cleanup (' + str(datetime.datetime.now()) + ')'
            actions = Action.query.filter(Action.date <= past)
            action_count = helpers.get_query_count(actions)
            print str(action_count) + ' items to cleanup'
            if action_count > 0:
                logentry = Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, 'Sync Master',
                               'syncmaster@roseguarden.org', 'Cleanup ' + str(action_count) + ' logs older than ' + str(ConfigManager.CLEANUP_THRESHOLD) + ' days', 'Cleanup',
                               'L1', 0, 'Internal')
                db.session.add(logentry)
            actions.delete()
            db.session.commit()
            print 'Next cleanup @' + str(next_time) + ' (' + str(datetime.datetime.now()) + ')'
            self.lastCleanupTime = now

    def backup_cycle(self):
        lasttime = self.lastBackupTime
        now = datetime.datetime.now()

        compare_time = lasttime.replace(hour=4, minute=35, second=0, microsecond=0)
        if compare_time > lasttime:
            next_time = compare_time
        else:
            next_time = compare_time + datetime.timedelta(days=1)

        if now > next_time or self.forceBackup == True:
            self.forceBackup = False
            print 'Doing a backup (' + str(datetime.datetime.now()) + ')'
            with app.app_context():
                flask_alchemydumps.autoclean(True)
                flask_alchemydumps.create()
                if ConfigManager.BACKUP_ENABLE_FTP == True:
                    print 'Doing a additional FTP backup'
                    app.config['ALCHEMYDUMPS_FTP_SERVER'] = ''
                    app.config['ALCHEMYDUMPS_FTP_USER'] = ''
                    app.config['ALCHEMYDUMPS_FTP_PASSWORD'] = ''
                    app.config['ALCHEMYDUMPS_FTP_PATH'] = ''
                    flask_alchemydumps.create()
                    app.config['ALCHEMYDUMPS_FTP_SERVER'] = ConfigManager.ALCHEMYDUMPS_FTP_SERVER
                    app.config['ALCHEMYDUMPS_FTP_USER'] = ConfigManager.ALCHEMYDUMPS_FTP_USER
                    app.config['ALCHEMYDUMPS_FTP_PASSWORD'] = ConfigManager.ALCHEMYDUMPS_FTP_PASSWORD
                    app.config['ALCHEMYDUMPS_FTP_PATH'] = ConfigManager.ALCHEMYDUMPS_FTP_PATH
            print 'Next backup @' + str(next_time) + ' (' + str(datetime.datetime.now()) + ')'
            logentry = Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, 'Sync Master',
                           'syncmaster@roseguarden.org', 'Backup database', 'Backup',
                           'L1', 0, 'Internal')
            db.session.add(logentry)
            db.session.commit()
            self.lastBackupTime = now

    def update_users_and_actions(self):
        actions = Action.query.filter_by(synced=0).order_by(Action.date).all()
        users = User.query.all()
        userDict = {}
        try:
            statDict_NodeAccess = {}
            statDict_UserCount = [0,0,0]
            statDict_Accesses = {}
            statDict_Weekdays = [0,0,0,0,0,0,0]

            for user in users:
                # create dictionary with indices
                userDict[str(user.email)] = users.index(user)

                # checking for invalid type in stored user-data
                if user.monthlyAccessCount is None:
                    user.monthlyAccessCount = 0
                if user.monthlyAccessAverage is None:
                    user.monthlyAccessAverage = 0
                if user.monthlyAccessMonthNumber is None:
                    user.monthlyAccessAverage = datetime.datetime.now().month

                # reset monthly access count for new month
                if user.monthlyAccessMonthNumber != datetime.datetime.now().month:
                    user.monthlyAccessCount = 0
                    user.monthlyAccessMonthNumber = datetime.datetime.now().month

                # update sync-date
                user.lastSyncDateTime = datetime.datetime.now()
                # check for
                if user.accessType == User.ACCESSTYPE_MONTHLY_BUDGET:
                    now = datetime.datetime.now()
                    lasttime = user.lastAccessDaysUpdateDate
                    compare_time = lasttime.replace(day=1, hour=0, minute=0, second=1, microsecond=0)
                    next_month_date = compare_time + relativedelta(months=1)
                    if now > next_month_date:
                        user.accessDayCounter = user.accessDayCyclicBudget
                        print 'update monthly day budget of ' + user.firstName + ' ' + user.lastName + '(' + user.email + ')' + ' to ' + str(user.accessDayCounter)
                        user.lastAccessDaysUpdateDate = now

                if user.accessType == User.ACCESSTYPE_QUARTERLY_BUDGET:
                    now = datetime.datetime.now()
                    lasttime = user.lastAccessDaysUpdateDate
                    compare_time = lasttime.replace(day=1, hour=0, minute=0, second=1, microsecond=0)
                    next_month_date = compare_time + relativedelta(months=1)

                    next_quarter_date = datetime.datetime.now()
                    if next_month_date.month > 10:
                        next_quarter_date = (next_month_date + relativedelta(years=1)).replace(month=1)
                    else:
                        if next_month_date.month > 7:
                            next_quarter_date = next_month_date.replace(month=10)
                        else:
                            if next_month_date.month > 4:
                                next_quarter_date = next_month_date.replace(month=7)
                            else:
                                next_quarter_date = next_month_date.replace(month=4)

                    if now > next_quarter_date:
                        user.accessDayCounter = user.accessDayCyclicBudget
                        print 'update quarterly day budget of ' + user.firstName + ' ' + user.lastName + '(' + user.email + ')' + ' to ' + str(user.accessDayCounter)
                        user.lastAccessDaysUpdateDate = now

                #SERIES_GENERALUSER = 0
                #SERIES_SUPERUSER = 1
                #SERIES_ADMINUSER = 2

                if user.syncMaster == 0:
                    if user.role == User.ROLE_USER:
                        statDict_UserCount[StatisticsManager.SERIES_GENERALUSER] += 1
                    if user.role == User.ROLE_ADMIN:
                        statDict_UserCount[StatisticsManager.SERIES_ADMINUSER] += 1
                    if user.role == User.ROLE_SUPERVISOR:
                        statDict_UserCount[StatisticsManager.SERIES_SUPERUSER] += 1

            for action in actions:
                action.synced = 1
                if action.action == Action.ACTION_OPENING_REQUEST:

                    try:
                        userIndex = userDict[str(action.userMail)]
                    except:
                        print "Skip User [" + str(userIndex) + "] for statistics, because the user got removed."
                        continue

                    users[userIndex].monthlyAccessCount += 1
                    delta = action.date - users[userIndex].lastAccessDateTime
                    if users[userIndex].accessType == User.ACCESSTYPE_ACCESS_DAYS or \
                        users[userIndex].accessType == User.ACCESSTYPE_MONTHLY_BUDGET or \
                        users[userIndex].accessType == User.ACCESSTYPE_QUARTERLY_BUDGET:
                        # check for opening request, happend at least 24 hours ago
                        if delta > datetime.timedelta(hours = 23, minutes=30, seconds=0):
                            if users[userIndex].lastAccessDateTime < action.date:
                                users[userIndex].lastAccessDateTime = action.date
                                users[userIndex].accessDayCounter -= 1
                                print 'update day counter of ' + users[userIndex].firstName + ' ' + users[userIndex].lastName + ' (' + users[userIndex].email + ')'

                    # update stat. dictionaries
                    if action.nodeName in statDict_NodeAccess:
                        statDict_NodeAccess[action.nodeName] += action.actionParameter
                    else:
                        statDict_NodeAccess[action.nodeName] = action.actionParameter

                    year = action.date.year
                    month = action.date.month
                    if year not in statDict_Accesses:
                        statDict_Accesses[year] = {}
                    if month not in statDict_Accesses[year]:
                        statDict_Accesses[year][month] = [0,0]

                    if action.authType == user.AUTHTYPE_WEB:
                        statDict_Accesses[year][month][StatisticsManager.SERIES_WEB_ACCESSES] += action.actionParameter
                    if action.authType == user.AUTHTYPE_RFID:
                        statDict_Accesses[year][month][StatisticsManager.SERIES_CARD_ACCESSES] += action.actionParameter

                    statDict_Weekdays[action.date.weekday()] += action.actionParameter

            statDict_monthlyAccessUserClasses = []
            for user in users:
                if user.syncMaster == 0:
                    statDict_monthlyAccessUserClasses.append(user.monthlyAccessCount)

            db.session.commit()

            if ConfigManager.STATISTICS_ENABLE == True:
                StatisticsManager.updateAccessesStat(statDict_Accesses)
                StatisticsManager.updateUserCountStat(statDict_UserCount)
                StatisticsManager.updateNodeAccessStat(statDict_NodeAccess)
                StatisticsManager.updateWeekdaysStat(statDict_Weekdays)
                StatisticsManager.updateUserActivityGroups(statDict_monthlyAccessUserClasses)
                StatisticsManager.updateUserActivityGroupAccesses(statDict_monthlyAccessUserClasses)
                StatisticsManager.updateUserActivityGroupAverages(statDict_monthlyAccessUserClasses)

        except:
            db.session.rollback()
            raise

    def sync_door_user(self, door):
        pwd = base64.b64decode(door.password)
        auth_token = 'Basic ' + base64.b64encode("syncmaster@roseguarden.org:" + pwd)
        headers = {'Authorization' : auth_token}

        if door.local != 1:
            if str(door.name) == ConfigManager.NODE_NAME:
                print 'warning: the node have the same node name'
            else:
                userList = User.query.filter_by(syncMaster=0).all()
                serial = UserSyncSerializer().dump(userList, many=True).data
                data = {'userList': serial}

                try:
                    request_address = str(door.address) + ":5000" + '/users'
                    response = requests.post(request_address, json= data, headers=headers, timeout=8)
                    print response
                except:
                    print "error while request users-sync"
                    raise

    def sync_door_log(self, door):
        pwd = base64.b64decode(door.password)
        auth_token = 'Basic ' + base64.b64encode("syncmaster@roseguarden.org:" + pwd)
        headers = {'Authorization' : auth_token}

        if door.local != 1:
            if str(door.name) == ConfigManager.NODE_NAME:
                print 'warning: the node have the same node name'
            else:
                request_address = str(door.address) + ":5000" + '/actions/admin'
                response = requests.get(request_address, headers= headers, timeout=8)
                print str(response)

                response_data = json.loads(response.content)
                actionList, errors = LogSerializer().loads(response.content, many=True)

                try:
                    db.session.add_all(actionList)
                    db.session.commit()
                except:
                    raise
                    return

                deletion_response = requests.delete(request_address, headers= headers, timeout=8)
                print deletion_response

    def sync_cycle(self):
        now = datetime.datetime.now()
        lasttime = self.lastSyncTime
        if ConfigManager.NODE_SYNC_CYCLIC == True:
            compare_time = lasttime + datetime.timedelta(minutes=ConfigManager.NODE_SYNC_CYCLE)
            if now > compare_time:
                self.lastSyncTime = now
                print 'Next sync @' + str(self.lastSyncTime + datetime.timedelta(minutes=ConfigManager.NODE_SYNC_CYCLE)) + ' (' + str(datetime.datetime.now()) + ')'
            else:
                if self.forceSync == True:
                    self.forceSync = False
                else:
                    return
        else:
            compare_time = lasttime.replace(hour=4, minute=15, second=0, microsecond=0)
            if compare_time > lasttime:
                next_time = compare_time
            else:
                next_time = compare_time + datetime.timedelta(days=1)

            if(now > next_time):
                self.lastSyncTime = now
                print 'Next sync @' + str(next_time) + ' (' + str(datetime.datetime.now()) + ')'
            else:
                if self.forceSync == True:
                    self.forceSync = False
                else:
                    return

        if ConfigManager.NODE_IS_MASTER == False:
            return

        print "Doing a sync cycle"

        linkedNodesList = NodeLink.query.all()

        for linkedNode in linkedNodesList:
            if linkedNode.local == 1:
                print 'Sync actions of ' + linkedNode.name + ' (local)'
            else:
                print 'Sync actions of ' + linkedNode.name
            self.sync_door_log(linkedNode)

        print 'Update actions'
        self.update_users_and_actions()
        logentry = Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, 'Sync Master', 'syncmaster@roseguarden.org',
                        'Update & synchronized actions and users',
                        'Update & Sync.', 'L1', 0, 'Internal')
        logentry.synced = 1
        db.session.add(logentry)
        db.session.commit()

        # sync user of all doors
        for linkedNode in linkedNodesList:
            if linkedNode.local == 1:
                print 'Sync user of ' + linkedNode.name + ' (local)'
            else:
                print 'Sync user of ' + linkedNode.name
            self.sync_door_user(linkedNode)
            if linkedNode.local == 0:
                logentry = Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, 'Sync Master', 'syncmaster@roseguarden.org',
                                'Synchronized ' + linkedNode.displayName + ' (' + linkedNode.name + ')',
                                'Synchronization', 'L1', 0, 'Internal')
                logentry.synced = 1
                db.session.add(logentry)
                db.session.commit()


    def led_cycle(self):
        if self.systemUp == True:
            GPIO.output(GPIO_LED_YELLOW, GPIO.HIGH)
        else:
            GPIO.output(GPIO_LED_YELLOW, GPIO.LOW)


        if self.ledState == self.LED_STATE_IDLE:
            self.ledStateCounter = 0

        if self.ledState == self.LED_STATE_ACCESS_GRANTED:
            if self.ledStateCounter % 2 == 0:
                GPIO.output(GPIO_LED_GREEN, GPIO.HIGH)
            else:
                GPIO.output(GPIO_LED_GREEN, GPIO.LOW)

            self.ledStateCounter += 1

            if self.ledStateCounter > 15:
                self.ledState = self.LED_STATE_IDLE
                self.ledStateCounter = 0

        if self.ledState == self.LED_STATE_ACCESS_DENIED:
            if self.ledStateCounter % 2 == 0:
                GPIO.output(GPIO_LED_RED, GPIO.HIGH)
            else:
                GPIO.output(GPIO_LED_RED, GPIO.LOW)

            self.ledStateCounter += 1

            if self.ledStateCounter > 15:
                self.ledState = self.LED_STATE_IDLE
                self.ledStateCounter = 0

        if self.ledState == self.LED_STATE_CLOSED:
            self.ledState = self.LED_STATE_IDLE
            self.ledStateCounter = 0
            GPIO.output(GPIO_LED_RED, GPIO.LOW)
            GPIO.output(GPIO_LED_GREEN, GPIO.LOW)


    def open_the_door(self):
        while(True):
            print "Openening door"
            time.sleep(1.0)
            GPIO.output(GPIO_RELAY, GPIO.LOW)
            GPIO.output(GPIO_LED_GREEN, GPIO.HIGH)

    def timer_cycle(self):
        self.thr = threading.Timer(0.6, BackgroundWorker.timer_cycle, [self])
        self.thr.start()

        self.requestTimer += 1

        if self.requestTimer >= 4:
            self.requestTimer = 0
            try:
               self.checkRFIDTag()
            except Exception, e:
                import traceback
                print traceback.format_exc()
                logentry = Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, 'Background Worker', 'background@roseguarden.org',
                                'Error: ' + str(traceback.format_exc()),
                                'Error occured', 'L1', 0, 'Internal')
                db.session.add(logentry)
                db.session.commit()

        self.backupTimer += 1
        if self.backupTimer > 113 or self.forceBackup == True:
            self.backupTimer = 0
            try:
                self.backup_cycle()
            except Exception, e:
                import traceback
                print traceback.format_exc()
                logentry = Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, 'Sync Master', 'syncmaster@roseguarden.org',
                                'Error: ' + str(traceback.format_exc()),
                                'Error occured', 'L1', 0, 'Internal')
                db.session.add(logentry)
                db.session.commit()

        self.syncTimer += 1
        if self.syncTimer > 155 or self.forceSync == True:
            self.syncTimer = 0
            # if syncing is force wait some time to prevent pipe-breaking
            if self.forceSync == True:
                time.sleep(1.0)
            try:
                if(ExtensionManager.extension.CONFIG_DISABLE_SYNC_CYCLES == False):
                    self.sync_cycle()
            except Exception, e:
                import traceback
                print traceback.format_exc()
                logentry = Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, 'Sync Master', 'syncmaster@roseguarden.org',
                                'Error: ' + str(traceback.format_exc()),
                                'Error occured', 'L1', 0, 'Internal')
                db.session.add(logentry)
                db.session.commit()

        self.cleanupTimer +=1
        if self.cleanupTimer > 205:
            self.cleanupTimer = 0
            if ConfigManager.CLEANUP_EANBLE == True:
                try:
                    if (ExtensionManager.extension.CONFIG_DISABLE_CLEANUP_CYLCES == False):
                        self.cleanup_cycle()
                except Exception, e:
                    import traceback
                    print traceback.format_exc()
                    logentry = Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, 'Sync Master', 'syncmaster@roseguarden.org',
                                    'Error: ' + str(traceback.format_exc()),
                                    'Error occured', 'L1', 0, 'Internal')
                    db.session.add(logentry)
                    db.session.commit()


        # print "Check for opening request"
        if self.requestOpening == True:
            self.requestOpening = False
            self.openingTimer = 0;
            print "Opening request"

        if self.openingTimer >= 0:
            if self.openingTimer == 0:
                print "Openening door"
            GPIO.output(GPIO_RELAY, GPIO.LOW)

            self.openingTimer += 1
            if self.openingTimer >= ConfigManager.DOOR_OPENING_TIME:
                self.openingTimer = -1
                print "Closing door"
                GPIO.output(GPIO_RELAY, GPIO.HIGH)
                self.ledState = self.LED_STATE_CLOSED
        else:
            GPIO.output(GPIO_RELAY, GPIO.HIGH)

        self.ledStateTimer += 1
        if self.ledStateTimer >= 0:
            self.ledStateTimer = 0
            try:
                self.led_cycle()
            except Exception, e:
                import traceback
                print traceback.format_exc()
                logentry = Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, 'Sync Master', 'syncmaster@roseguarden.org',
                                'Error: ' + str(traceback.format_exc()),
                                'Error occured', 'L1', 0, 'Internal')
                db.session.add(logentry)
                db.session.commit()


    def cancel(self):
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            self.thr.cancel()


backgroundWorker = BackgroundWorker(app)
