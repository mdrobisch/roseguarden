__author__ = 'drobisch'

from models import User
from server import app
import threading
import os

from RFID import RFID
from RFID import RFIDMockup

from GPIO import GPIO
from GPIO import GPIOMockup

class BackgroundWorker():
    def __init__(self, app):
        # initialize worker variables
        self.app = app
        self.requestOpening = False;
        self.openingTimer = -1;

        # setup gpio and set default (Low)
        GPIO.setup(7,GPIO.OUT)
        GPIO.output(7, GPIO.LOW)

    def run(self):
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            self.thr = threading.Timer(1, self.timer_cycle)
            self.thr.start()
            print 'started background-server'

    def timer_cycle(self):
        self.thr = threading.Timer(1, BackgroundWorker.timer_cycle,[self])
        self.thr.start()
        if self.requestOpening == True:
            self.requestOpening = False
            self.openingTimer = 0;
            print "Opening request"

        if self.openingTimer >= 0:
            print "Opened door cycle" + "("  + ")"
            GPIO.output(7, GPIO.HIGH)
            self.openingTimer += 1
            if self.openingTimer >= 5:
                self.openingTimer = -1
                print "Closing door"
                GPIO.output(7, GPIO.LOW)

        #else:
            #print "Closing door"

        #user = User.query.filter_by(id=0).first()
        #print user.firstName

    def cancel(self):
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            self.thr.cancel()

backgroundWorker = BackgroundWorker(app)
