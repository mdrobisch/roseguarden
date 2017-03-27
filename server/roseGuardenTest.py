import codecs
import sys
from sys import version_info

from flask import Flask
from flask_script import Manager
#!/usr/bin/env python
# -*- coding: utf8 -*-

from app.drivers.authentication.RFID import RFIDReader
import signal

stopTest = False

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

# Capture SIGINT for cleanup when the script is aborted
def endTest(signal,frame):
    global stopTest
    print "Ctrl+C captured, ending test."
    stopTest = True

def getInput(text):
    py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2

    if py3:
        return input(text)
    else:
        return raw_input(text)

signal.signal(signal.SIGINT, endTest)

app = Flask(__name__)

manager = Manager(app, False)

@manager.command
def testRfidRead():
    "Test reading of an empty, unassigned rfid tag"

    global stopTest
    print "Test reading of rfid tag (stop testing with Ctrl+C)"
    while (stopTest == False):

        # Scan for cards
        (status,TagType) = RFIDReader.MFRC522_Request(RFIDReader.PICC_REQIDL)

        # If a card is found
        if status == RFIDReader.MI_OK:
            print "Card detected"

        # Get the UID of the card
        (status,uid) = RFIDReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == RFIDReader.MI_OK:

            # Print UID
            print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])

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
            else:
                print "Authentication error"

if __name__ == '__main__':
    manager.run()

