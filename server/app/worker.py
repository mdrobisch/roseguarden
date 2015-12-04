__author__ = 'drobisch'

from models import User
from server import app
import threading
import time
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
        self.tagInfo = RfidTagInfo("", "")
        self.tagResetCount = 0
        self.lock = False


        # setup gpio and set default (Low)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12,GPIO.OUT, initial=GPIO.HIGH)
        GPIO.output(12, GPIO.HIGH)


    def run(self):
        #if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        self.thr = threading.Timer(1, self.timer_cycle)
        self.thr.start()
        print 'started background-server'

    def resetTagInfo(self):
        self.tagInfo.tagId = ""
        self.tagInfo.userInfo = ""

    def withdrawRFIDTag(self, user):
        while(self.lock == True):
            print "still locked (withdrawRFIDTag)"
            time.sleep(0.15)

        self.lock = True

        print "background-worker withdrawRFIDTag"

        (status, TagType) = RFIDReader.MFRC522_Request(RFIDReader.PICC_REQIDL)

        (status, uid) = RFIDReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == RFIDReader.MI_OK:
            # Print UID
            uid_str = str(uid[0])+"." +str(uid[1])+"."+str(uid[2])+"."+str(uid[3])
            print "Card read UID: " + uid_str

            if (uid_str != user.cardID):
                print "Wrong cardID detected while withdrawing RFID-tag to user"
                self.lock = False
                return False

            # This is the default key for authentication
            defaultkey = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
            defaultsecret = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

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
            if status == RFIDReader.MI_OK :
                print "Read TrailerBlock :"
                # Read block 8
                result = RFIDReader.MFRC522_Read(TrailerBlockAddr)
                print result

                for x in range(0,6):
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
            self.lock = False
            return False

    def assignRFIDTag(self, user):
        while(self.lock == True):
            print "still locked (assignRFIDTag)"
            time.sleep(0.15)

        self.lock = True

        print "background-worker assignRFIDTag"

        (status, TagType) = RFIDReader.MFRC522_Request(RFIDReader.PICC_REQIDL)

        (status, uid) = RFIDReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == RFIDReader.MI_OK:
            # Print UID
            uid_str = str(uid[0])+"." +str(uid[1])+"."+str(uid[2])+"."+str(uid[3])
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

                for x in range(0,6):
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

    def checkRFIDTag(self):
        while(self.lock == True):
            print "still locked (checkRFIDTag)"
            time.sleep(0.15)

        self.lock = True

        (status, TagType) = RFIDReader.MFRC522_Request(RFIDReader.PICC_REQIDL)

        # If a card is found
        #if status == RFIDReader.MI_OK:
        #    print "rfid tag detected"

        # Get the UID of the card
        (status, uid) = RFIDReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == RFIDReader.MI_OK:

            # Print UID

            self.tagInfo.tagId = str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3])
            self.tagInfo.userInfo = ""

            user = User.query.filter_by(cardID=self.tagInfo.tagId).first()

            if user is None:
                print "No user asigned to card"
                self.lock = False
                return

            self.tagInfo.userInfo = user.email
            print user.email

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

            # Authenticate
            status = RFIDReader.MFRC522_Auth(RFIDReader.PICC_AUTHENT1A, SecretBlockAddr, userkey, uid)

            # Check if authenticated
            if status == RFIDReader.MI_OK:

                readSecret = RFIDReader.MFRC522_Read(SecretBlockAddr)
                print readSecret
                readSecretString = ''
                i = 0

                for x in readSecret:
                    if i != 0:
                        hexstr = hexstr + '-'
                    i = i + 1
                    readSecretString = readSecretString + format(x, '02X')

                print readSecretString

                if readSecretString == user.cardSecret:
                    print "correct secret"
                    if user.checkUserAccessPrivleges() == "access granted":
                        print "no user-access privilege"
                        self.requestOpening = True

                RFIDReader.MFRC522_StopCrypto1()
                self.lock = False
                return True
            else:
                self.tagInfo.userInfo = user.email + '(invalid)'
                print "Authentication error"
                self.lock = False
                return False
        else:
            self.lock = False
            return False

    def timer_cycle(self):
        self.thr = threading.Timer(1, BackgroundWorker.timer_cycle,[self])
        self.thr.start()

        self.requestTimer += 1

        if self.requestTimer >= 2:
            self.requestTimer = 0
            self.resetTagInfo()
            self.checkRFIDTag()

        #print "Check for opening request"
        if self.requestOpening == True:
            self.requestOpening = False
            self.openingTimer = 0;
            print "Opening request"

        if self.openingTimer >= 0:
            print "Opened door cycle" + "("  + ")"
            GPIO.output(12, GPIO.LOW)
            self.openingTimer += 1
            if self.openingTimer >= 7:
                self.openingTimer = -1
                print "Closing door"
                GPIO.output(12, GPIO.HIGH)


        #else:
            #print "Closing door"

        #user = User.query.filter_by(id=0).first()
        #print user.firstName

    def cancel(self):
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            self.thr.cancel()

backgroundWorker = BackgroundWorker(app)
