import requests

__author__ = 'drobisch'

import flask_alchemydumps
from models import User, Door
from server import app, db
from serializers import LogSerializer, UserSyncSerializer, SessionInfoSerializer, DoorSerializer, RfidTagInfoSerializer
from werkzeug.datastructures import MultiDict
import threading
import time
import config
import json
import datetime
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
        self.backupTimer = 0
        self.tagInfo = RfidTagInfo("", "")
        self.tagResetCount = 0
        self.lock = False
        self.lastBackupTime = datetime.datetime.now()
        self.lastSynchronitationTime = datetime.datetime.now()
        # setup gpio and set default (Low)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.output(12, GPIO.HIGH)

    def run(self):
        # if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        self.thr = threading.Timer(1, self.timer_cycle)
        self.thr.start()
        # [('accessTimeStart', 'Sat, 05 Dec 2015 06:00:00 -0000'), ('firstName', u'Sync'), ('lastName', u'Master'), ('accessDayCounter', 0), ('cardID', u''), ('accessType', 0), ('accessDateStart', 'Sat, 05 Dec 2015 00:00:00 -0000'), ('keyMask', 0), ('email', u'syncmaster@roseguarden.org'), ('phone', u'0'), ('accessDaysMask', 127), ('role', 1), ('licenseMask', 0), ('lastLoginDateTime', 'Sat, 05 Dec 2015 00:26:47 -0000'), ('accessDateEnd', 'Sun, 01 Dec 2030 00:00:00 -0000'), ('budget', 0.0), ('accessTimeEnd', 'Sat, 05 Dec 2015 22:30:00 -0000'), ('registerDateTime', 'Sat, 05 Dec 2015 00:26:47 -0000'), ('id', 1), ('association', u'')]), OrderedDict([('accessTimeStart', 'Sat, 05 Dec 2015 06:00:00 -0000'), ('firstName', u'Konglomerat'), ('lastName', u'Kommando'), ('accessDayCounter', 0), ('cardID', u''), ('accessType', 1), ('accessDateStart', 'Sat, 05 Dec 2015 00:00:00 -0000'), ('keyMask', 0), ('email', u'kommando@konglomerat.org'), ('phone', u'0'), ('accessDaysMask', 127), ('role', 0), ('licenseMask', 0), ('lastLoginDateTime', 'Sat, 05 Dec 2015 00:26:47 -0000'), ('accessDateEnd', 'Sun, 01 Dec 2030 00:00:00 -0000'), ('budget', 0.0), ('accessTimeEnd', 'Sat, 05 Dec 2015 22:30:00 -0000'), ('registerDateTime', 'Sat, 05 Dec 2015 00:26:47 -0000'), ('id', 2), ('association', u'')]), OrderedDict([('accessTimeStart', 'Sat, 05 Dec 2015 06:00:00 -0000'), ('firstName', u'Marcus'), ('lastName', u'Drobisch'), ('accessDayCounter', 0), ('cardID', u''), ('accessType', 1), ('accessDateStart', 'Sat, 05 Dec 2015 00:00:00 -0000'), ('keyMask', 3), ('email', u'm.drobisch@googlemail.com'), ('phone', u'01754404298'), ('accessDaysMask', 127), ('role', 1), ('licenseMask', 0), ('lastLoginDateTime', 'Sat, 05 Dec 2015 00:26:48 -0000'), ('accessDateEnd', 'Sun, 01 Dec 2030 00:00:00 -0000'), ('budget', 0.0), ('accessTimeEnd', 'Sat, 05 Dec 2015 22:30:00 -0000'), ('registerDateTime', 'Sat, 05 Dec 2015 00:26:48 -0000'), ('id', 3), ('association', u'')]
        print 'started background-server'

    def resetTagInfo(self):
        self.tagInfo.tagId = ""
        self.tagInfo.userInfo = ""

    def checkBackupHandle(self):
        print "check for next backup"

    def checkLogUpdaterHandle(self):
        print "check for next log update"

    def checkSynchronizerHandle(self):
        print "check for next synchronizer update"

    def withdrawRFIDTag(self, user):
        while (self.lock == True):
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
                        if user.checkUserAccessPrivleges() == "access granted":
                            self.requestOpening = True
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

    def backup_cycle(self):
        lasttime = self.lastBackupTime
        now = datetime.datetime.now()

        compare_time = lasttime.replace(hour=4, minute=00, second=0, microsecond=0)
        if compare_time > lasttime:
            next_time = compare_time
        else:
            next_time = compare_time + datetime.timedelta(days=1)

        if(now > next_time):
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
            self.lastBackupTime = now

    def sync_cycle(self):
        print "sync cycle"
        door = Door.query.filter_by(id=0).first()
        doorList = Door.query.all()

        for doorSync in doorList:
            print doorSync.name

        userList = User.query.filter_by(syncMaster=0).all()
        adding = 0

        if adding == 1:
            newUser = User("test" + str(datetime.datetime.now().hour) + '-' +  str(datetime.datetime.now().minute) + '-' + str(datetime.datetime.now().second) + "@gmx.de", "test", "newuser", "lastuser")
            newUser.id = -1
            userList.append(newUser)
        else:
            tempUserList = []
            for usr in userList:
                if userList.index(usr) < 2:
                    tempUserList.append(usr)
            userList = tempUserList

        serial = UserSyncSerializer().dump(userList, many=True).data
        print serial
        data = {'userList' : serial}
        try:
            response = requests.post('http://localhost:5000' + '/users', json= data, timeout=4)
            print response
        except:
            print "error while request users-sync"

    def timer_cycle(self):
        self.thr = threading.Timer(1, BackgroundWorker.timer_cycle, [self])
        self.thr.start()

        self.requestTimer += 1

        if self.requestTimer >= 3:
            self.requestTimer = 0
            self.checkRFIDTag()

        self.backupTimer += 1
        if self.backupTimer > 60:
            self.backupTimer = 0;
            self.backup_cycle()

        self.syncTimer += 1
        if self.syncTimer > 3:
            self.syncTimer = -100000
            self.sync_cycle()

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
