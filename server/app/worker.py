__author__ = 'drobisch'

from models import User
from server import app
import threading
import os

class BackgroundWorker():
    def __init__(self, app):
        self.app = app
        self.requestOpening = False;
        self.openingTimer = -1;


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
            self.openingTimer += 1
            if self.openingTimer >= 5:
                self.openingTimer = -1
                print "Closing door"
        #else:
            #print "Closing door"

        #user = User.query.filter_by(id=0).first()
        #print user.firstName

    def cancel(self):
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            self.thr.cancel()

backgroundWorker = BackgroundWorker(app)
