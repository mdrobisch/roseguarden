__author__ = 'drobisch'

import platform

class RFIDStateMockup:

    def __init__(self):
        print "RFID: Init mockup"
        return None

class RFIDWrapper:

    def __init__(self):
        print "RFID: Init wrapper"
        return None

if platform.platform_getType() == platform.RASPBERRY_PI:
    try:
        import MFRC522 as RFID
        print "RFID: Using MFRC522 as RFID"
        RFIDMockup = None
    except RuntimeError:
        print(
            "Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
else:
    print "RFID: Using RFIDWrapper as RFID"
    RFID = RFIDWrapper()
    RFIDMockup = RFIDStateMockup()
