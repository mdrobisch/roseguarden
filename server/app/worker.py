import requests

__author__ = 'drobisch'

import flask_alchemydumps
from models import User, Door, Action
from server import app, db
from serializers import LogSerializer, UserSyncSerializer, SessionInfoSerializer, DoorSerializer, RfidTagInfoSerializer
from werkzeug.datastructures import MultiDict
import threading
import time
import config
import base64
import json
import datetime
from dateutil.relativedelta import relativedelta
import os
from models import RfidTagInfo
from RFID import RFIDReader
from RFID import RFIDMockup
from GPIO import GPIO
from GPIO import GPIOMockup


class BackgroundWorker():
    def __init__(self, app):
        # initialize worker variables
        self.app = app
        self.requestOpening = False
        self.openingTimer = -1
        self.requestTimer = 0
        self.syncTimer = 0
        if config.NODE_SYNC_ON_STARTUP == True:
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
        self.lastCleanupTime = datetime.datetime.now()
        self.lastSyncTime = datetime.datetime.now()
        # setup gpio and set default (Low)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.output(12, GPIO.HIGH)

    def run(self):
        # if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        self.thr = threading.Timer(1, self.timer_cycle)

        self.update_users_and_actions()

        self.thr.start()
        print 'started background-server ' + '(' + str(datetime.datetime.now()) + ')'

    def resetTagInfo(self):
        self.tagInfo.tagId = ""
        self.tagInfo.userInfo = ""

    def withdrawRFIDTag(self, user):
        while (self.lock == True):
            if config.DEBUG == False:
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
                self.tagInfo.tagId = str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3])
                self.tagInfo.userInfo = ""

                user = User.query.filter_by(cardID=self.tagInfo.tagId).first()

                if user is None:
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

                    for x in readSecret:
                        if i != 0:
                            readSecretString = readSecretString + '-'
                        i = i + 1
                        readSecretString = readSecretString + format(x, '02X')

                    # print readSecretString

                    if readSecretString == user.cardSecret:
                        print "correct secret"
                        if user.checkUserAccessPrivleges() == "Access granted.":
                            self.requestOpening = True
                            logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, user.firstName + ' ' + user.lastName,
                                           user.email, 'Opening request', 'Opening request',
                                           'L2', 1, 'Card based', Action.ACTION_OPENING_REQUEST)
                            db.session.add(logentry)
                            db.session.commit()
                        else:
                            print "no user-access privilege"
                    else:
                        self.tagInfo.userInfo = user.email + '(inv. sec.)'
                        print "no user-access privilege"

                    RFIDReader.MFRC522_StopCrypto1()
                    self.lock = False
                    return True
                else:
                    self.tagInfo.userInfo = user.email + '(inv. key.)'
                    print "Authentication error"
                    self.lock = False
                    return False
            else:
                self.lock = False
                return False
        except:
            self.lock = False
            print "unexpected error in checkRFIDTag"
            raise

    def cleanup_cycle(self):
        lasttime = self.lastCleanupTime
        now = datetime.datetime.now()
        past = now - datetime.timedelta(days=config.CLEANUP_THRESHOLD)

        compare_time = lasttime.replace(hour=04, minute=55, second=0, microsecond=0)
        if compare_time > lasttime:
            next_time = compare_time
        else:
            next_time = compare_time + datetime.timedelta(days=1)

        if(now > next_time):
            print 'Doing a cleanup (' + str(datetime.datetime.now()) + ')'
            Action.query.filter(Action.date <= past).delete()
            logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, 'Sync Master',
                           'syncmaster@roseguarden.org', 'Cleanup logs older than ' + str(config.CLEANUP_THRESHOLD) + ' days', 'Cleanup',
                           'L1', 0, 'Internal')
            db.session.add(logentry)
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
                if config.BACKUP_ENABLE_FTP == True:
                    print 'Doing a additional FTP backup'
                    app.config['ALCHEMYDUMPS_FTP_SERVER'] = ''
                    app.config['ALCHEMYDUMPS_FTP_USER'] = ''
                    app.config['ALCHEMYDUMPS_FTP_PASSWORD'] = ''
                    app.config['ALCHEMYDUMPS_FTP_PATH'] = ''
                    flask_alchemydumps.create()
                    app.config['ALCHEMYDUMPS_FTP_SERVER'] = config.ALCHEMYDUMPS_FTP_SERVER
                    app.config['ALCHEMYDUMPS_FTP_USER'] = config.ALCHEMYDUMPS_FTP_USER
                    app.config['ALCHEMYDUMPS_FTP_PASSWORD'] = config.ALCHEMYDUMPS_FTP_PASSWORD
                    app.config['ALCHEMYDUMPS_FTP_PATH'] = config.ALCHEMYDUMPS_FTP_PATH
            print 'Next backup @' + str(next_time) + ' (' + str(datetime.datetime.now()) + ')'
            logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, 'Sync Master',
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
            for user in users:
                # create dictionary with indices
                userDict[str(user.email)] = users.index(user)
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

            for action in actions:
                action.synced = 1
                if action.action == Action.ACTION_OPENING_REQUEST:
                    userIndex = userDict[str(action.userMail)]
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
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def sync_door_user(self, door):
        pwd = base64.b64decode(door.password)
        auth_token = 'Basic ' + base64.b64encode("syncmaster@roseguarden.org:" + pwd)
        headers = {'Authorization' : auth_token}

        if door.local != 1:
            if str(door.name) == config.NODE_NAME:
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
            if str(door.name) == config.NODE_NAME:
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
        if config.NODE_SYNC_CYCLIC == True:
            compare_time = lasttime + datetime.timedelta(minutes=config.NODE_SYNC_CYCLE)
            if now > compare_time:
                self.lastSyncTime = now
                print 'Next sync @' + str(self.lastSyncTime + datetime.timedelta(minutes=config.NODE_SYNC_CYCLE)) + ' (' + str(datetime.datetime.now()) + ')'
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

        if config.NODE_MASTER == False:
            return

        print "Doing a sync cycle"

        doorList = Door.query.all()

        for doorSync in doorList:
            if doorSync.local == 1:
                print 'Sync actions of ' + doorSync.name + ' (local)'
            else:
                print 'Sync actions of ' + doorSync.name
            self.sync_door_log(doorSync)

        print 'Update actions'
        self.update_users_and_actions()
        logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, 'Sync Master', 'syncmaster@roseguarden.org',
                        'Update & synchronized actions and users',
                        'Update & Sync.', 'L1', 0, 'Internal')
        logentry.synced = 1
        db.session.add(logentry)
        db.session.commit()

        for doorSync in doorList:
            if doorSync.local == 1:
                print 'Sync user of ' + doorSync.name + ' (local)'
            else:
                print 'Sync user of ' + doorSync.name
            self.sync_door_user(doorSync)
            if doorSync.local == 0:
                logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, 'Sync Master', 'syncmaster@roseguarden.org',
                                'Synchronized ' + doorSync.displayName + ' (' + doorSync.name + ')',
                                'Synchronization', 'L1', 0, 'Internal')
                logentry.synced = 1
                db.session.add(logentry)
                db.session.commit()

    def open_the_door(self):

        while(True):
            print "Openening door"
            time.sleep(1.0)
            GPIO.output(12, GPIO.LOW)

    def timer_cycle(self):
        self.thr = threading.Timer(1.5, BackgroundWorker.timer_cycle, [self])
        self.thr.start()

        self.requestTimer += 1

        if self.requestTimer >= 2:
            self.requestTimer = 0
            self.checkRFIDTag()

        self.backupTimer += 1
        if self.backupTimer > 113 or self.forceBackup == True:
            self.backupTimer = 0
            self.backup_cycle()

        self.syncTimer += 1
        if self.syncTimer > 55 or self.forceSync == True:
            self.syncTimer = 0
            # if syncing is force wait some time to prevent pipe-breaking
            if self.forceSync == True:
                time.sleep(1.0)
            self.sync_cycle()

        self.cleanupTimer +=1
        if self.cleanupTimer > 121:
            self.cleanupTimer = 0
            if config.CLEANUP_EANBLE == True:
                self.cleanup_cycle()

        # print "Check for opening request"
        if self.requestOpening == True:
            self.requestOpening = False
            self.openingTimer = 0;
            print "Opening request"

        if self.openingTimer >= 0:
            if self.openingTimer == 0:
                print "Openening door"
            GPIO.output(12, GPIO.LOW)
            self.openingTimer += 1
            if self.openingTimer >= 7:
                self.openingTimer = -1
                print "Closing door"
                GPIO.output(12, GPIO.HIGH)

                # else:
                # print "Closing door"

                # user = User.query.filter_by(id=0).first()
                # print user.firstName

    def cancel(self):
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            self.thr.cancel()


backgroundWorker = BackgroundWorker(app)
