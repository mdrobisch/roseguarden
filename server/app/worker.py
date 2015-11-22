__author__ = 'drobisch'

from models import User
from server import app
import threading
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



    def assignRFIDTag(self, user, rfidID):

        self.lock = True

        print "background-worker assign"

        (status,TagType) = RFIDReader.MFRC522_Request(RFIDReader.PICC_REQIDL)

        (status,uid) = RFIDReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == RFIDReader.MI_OK:

            # Print UID
            print "Card read UID: "+str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3])

            self.tagInfo.tagId = str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3])
            self.tagInfo.userInfo = ""

            # This is the default key for authentication
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

            # Select the scanned tag
            RFIDReader.MFRC522_SelectTag(uid)

            # Authenticate
            status = RFIDReader.MFRC522_Auth(RFIDReader.PICC_AUTHENT1A, 8, key, uid)

            # Check if authenticated
            if status == RFIDReader.MI_OK:
                RFIDReader.MFRC522_Read(8)
                RFIDReader.MFRC522_StopCrypto1()
                self.lock = False
                return True
            else:
                print "Authentication error"
                self.lock = False
                return False

        self.lock = False
        return False

    def readRFIDTag(self):

        self.lock = True

        (status,TagType) = RFIDReader.MFRC522_Request(RFIDReader.PICC_REQIDL)

        # If a card is found
        #if status == RFIDReader.MI_OK:
        #    print "rfid tag detected"

        # Get the UID of the card
        (status,uid) = RFIDReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == RFIDReader.MI_OK:

            # Print UID
            #print "Card read UID: "+str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3])

            self.tagInfo.tagId = str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3])
            self.tagInfo.userInfo = ""

            # This is the default key for authentication
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

            # Select the scanned tag
            RFIDReader.MFRC522_SelectTag(uid)

            # Authenticate
            status = RFIDReader.MFRC522_Auth(RFIDReader.PICC_AUTHENT1A, 8, key, uid)

            # Check if authenticated
            if status == RFIDReader.MI_OK:
                user = User.query.filter_by(cardID=self.tagInfo.tagId).first()
                if user is None:
                    print "No user asigned to card"
                else:
                    self.tagInfo.userInfo = user.email
                    if user.checkUserAccessPrivleges() == "access granted":
                        self.requestOpening = True
                    print user.email

                RFIDReader.MFRC522_StopCrypto1()
                self.lock = False
                return True
            else:
                print "Authentication error"
                self.lock = False
                return False

        self.lock = False
        return False

    def timer_cycle(self):
        self.thr = threading.Timer(1, BackgroundWorker.timer_cycle,[self])
        self.thr.start()

        self.requestTimer += 1

        if self.requestTimer >= 2:
            self.requestTimer = 0
            self.resetTagInfo()
            self.readRFIDTag()

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
