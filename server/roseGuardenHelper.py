import codecs
import time

import datetime

import sys
from flask import Flask
from flask_script import Manager, Option
from sys import version_info
from app.server import app, db
from app.worker import backgroundWorker
from app.models import User

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

app = Flask(__name__)

manager = Manager(app, False)


def getInput(text):
    py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2

    if py3:
      return input(text)
    else:
      return raw_input(text)


@manager.command
def deleteUser():
    #print "Test: " +  str(getInput("Please enter your name: "))

    "Start RoseGuarden"
    # start backgroundworker
    backgroundWorker.run()

    # running the flask app
    app.run('0.0.0.0', threaded=True)

    # after exiting the app, cancel the backgroundowrker
    backgroundWorker.cancel()

@manager.command
def openDoor():
    "Force the local door openend"
    backgroundWorker.run()
    backgroundWorker.open_the_door()
    time.sleep(10)
    backgroundWorker.cancel()

@manager.command
@manager.option('-c', '--csv', dest='csv', default='?')
def updateList(csv):
    "Update userlist from a csv-file"
    print "Update user list"

@manager.command
def updateAssociation():

    stop = False
    while stop is False:
        association = getInput("Please enter the association-group to update: ")
        users = User.query.filter_by(association=association).all()

        print ""
        print "The association contains the following members:"

        if users == []:
            print "\tNo members in the assocation."
        else:
            for user in users:
                print "\t", (user.firstName), " ", (user.lastName), " - ", (user.email)

            print ""

            change = getInput("Do you like to change the access of the association? (y/n) : ")

            print ""

            if change == 'y':
                print "Enter new data for the members in the association, press return to let the values untouched."
                accesTypeString = getInput('\tEnter one of the following access-types \n\r \t\tNO_ACCESS = 0\n\r \t\tDAILY_ACCESS_PERIOD = 1\n\r \t\tACCESS_DAYS_BUDGET = 2\n\r \t\tLIFETIME_ACCESS = 3\n\r \t\tMONTHLY_BUDGET = 4\n\r \t\tQUARTERLY_BUDGET = 5\n\r \tenter type-number:')
                if accesTypeString != "":
                    accessType = int(accesTypeString)

                keyString = getInput("\tEnter new keys in the form of  '110010011' : ")
                if keyString != "":
                    keyMask = int(keyString,2)

                daysString = getInput("\tEnter new days in the form of '1010111' : ")
                if daysString != "":
                    dayMask = int(daysString,2)

                startDateString = getInput("\tEnter new date the access starts, in the form '2016-12-24' : ")
                if startDateString != "":
                    startDate = datetime.datetime.strptime(startDateString,"%Y-%m-%d")

                endDateString = getInput("\tEnter new date the access ends, in the form '2016-12-24' : ")
                if endDateString != "":
                    endDate = datetime.datetime.strptime(endDateString,"%Y-%m-%d")

                startTimeString = getInput("\tEnter new time the daily access starts, in the form '18:15' : ")
                if startTimeString != "":
                    startTime = datetime.datetime.strptime(startTimeString,"%H:%M")

                endTimeString = getInput("\tEnter new time the daily access ends, in the form '23:15' : ")
                if endTimeString != "":
                    endTime = datetime.datetime.strptime(endTimeString, "%H:%M")

                dayCounterString = getInput("\tEnter new actual day budget : ")
                if dayCounterString != "":
                    dayCounter = int(dayCounterString)

                dayCounterBudgetString = getInput("\tEnter new cyclic day budget : ")
                if dayCounterBudgetString != "":
                    dayCounterBudget = int(dayCounterBudgetString)

                print ""

                change = ""
                while(change == ""):
                    change = getInput("Do you like to change the access of the association? (y/n) : ")

                print ""

                if change == 'y':
                    for user in users:
                        if 'accessType' in locals():
                            print "change accessType of ", user.firstName, " ", user.lastName, " to ", accessType
                            user.accessType = accessType
                        if 'keyMask' in locals():
                            print "change keyMask of ", user.firstName, " ", user.lastName, " to ", keyMask
                            user.keyMask = keyMask
                        if 'dayMask' in locals():
                            print "change dayMask of ", user.firstName, " ", user.lastName, " to ", dayMask
                            user.accessDaysMask = dayMask
                        if 'startDate' in locals():
                            print "change startDate of ", user.firstName, " ", user.lastName, " to ", startDate.replace(hour=0,minute=0,second=0)
                            user.accessDateStart = startDate.replace(hour=0,minute=0,second=0)
                        if 'endDate' in locals():
                            print "change endDate of ", user.firstName, " ", user.lastName, " to ", endDate.replace(hour=23,minute=59,second=0)
                            user.accessDateEnd = endDate.replace(hour=23,minute=59,second=0)
                        if 'startTime' in locals():
                            print "change startTime of ", user.firstName, " ", user.lastName, " to ", startTime.time()
                            user.accessTimeStart = startTime
                        if 'endTime' in locals():
                            print "change endTime of ", user.firstName, " ", user.lastName, " to ", endTime.time()
                            user.accessTimeEnd = endTime
                        if 'dayCounter' in locals():
                            print "change dayCounter of ", user.firstName, " ", user.lastName, " to ", dayCounter
                            user.accessDayCounter = dayCounter
                        if 'dayCounterBudget' in locals():
                            print "change dayCounterBudget of ", user.firstName, " ", user.lastName, " to ", dayCounterBudget
                            user.accessDayCyclicBudget = dayCounterBudget

                        print ""

                    if 'accessType' in locals():
                        del accessType
                    if 'keyMask' in locals():
                        del keyMask
                    if 'dayMask' in locals():
                        del dayMask
                    if 'startDate' in locals():
                        del startDate
                    if 'endDate' in locals():
                        del endDate
                    if 'startTime' in locals():
                        del startTime
                    if 'endTime' in locals():
                        del endTime
                    if 'dayCounter' in locals():
                        del dayCounter
                    if 'dayCounterBudget' in locals():
                        del dayCounterBudget

                    db.session.commit()

        print ""

        if (getInput("Do you like to change another association? (y/n): ")) != 'y':
            break

        print ""

if __name__ == '__main__':
    manager.run()