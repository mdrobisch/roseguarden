__author__ = 'drobisch'
import string
import random
import datetime
import settings
from models import User
from collections import namedtuple


def generator_password(size=6, chars=string.ascii_uppercase + string.digits + string.lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

def checkUserAccessPrivleges(time,user):
    # check for invalid accessType == no access
    if (user.keyMask & settings.SETTING_NODE_VALID_KEYS_MASK) == 0:
        return 'Denied access because of unauthorized keys.'

    if user.accessType == user.ACCESSTYPE_NO_ACCESS or user.accessType > user.ACCESSTYPE_MAX:
        return 'Denied access because of unauthorized access type.'

    accessDateStart = user.accessDateStart.replace(hour=0, minute=0, second=0, microsecond=0)
    accessDateEnd = user.accessDateEnd.replace(hour=23, minute=59, second=59, microsecond=0)

    accessTimeStart = user.accessTimeStart.time()
    accessTimeEnd = user.accessTimeEnd.time()

    if accessTimeStart < accessTimeEnd:
        accessDateEndExtended = None
        print "accessDateEndExtended = none"
    else:
        accessDateEndExtended = accessDateEnd + datetime.timedelta(days=1)
        print "accessDateEndExtended = " + str(accessDateEndExtended)

    inDateEndExtention = False

    # check start-date and end-date for accessType == period
    if user.accessType == user.ACCESSTYPE_DAILY_ACCESS_PERIOD:
        if accessDateStart > time:
            return 'Denied access because of invalid start of period.'
        if accessDateEnd < time:
            if accessDateEndExtended == None:
                return 'Denied access because of invalid end of period.'
            else:
                if(accessDateEndExtended < time):
                    return 'Denied access because of invalid end of period.'
                else:
                    print "detected inDateEndExtention = True"
                    inDateEndExtention = True

    # check day counter for accessType == day-budget
    if user.accessType == user.ACCESSTYPE_ACCESS_DAYS:
        if user.accessDayCounter <= 0:
            return 'Denied access because of insufficient day-budget.'

    if inDateEndExtention == False:
        if (int(1 << time.weekday()) & user.accessDaysMask) == 0:
            return 'Denied access because of invalid access weekday.'
    else:
        print str((time - datetime.timedelta(days=1))) + " " + str((time + datetime.timedelta(days=1)).weekday())
        if (int(1 << (time - datetime.timedelta(days=1)).weekday()) & user.accessDaysMask) == 0:
            return 'Denied access because of invalid access weekday.'

    if inDateEndExtention == False:
        if accessDateEndExtended == None:
            if accessTimeStart > time.time():
                return 'Denied access because of invalid day-time start.'
            if accessTimeEnd <= time.time():
                return 'Denied access because of invalid day-time end.'
        else:
            if accessTimeStart > time.time():
                return 'Denied access because of invalid day-time start.'
    else:
        if accessTimeEnd <= time.time():
            print "extended end check failed"
            return 'Denied access because of invalid day-time end.'

    return "Access granted."

def securityTests():
    testCase = namedtuple('testCase', ['keyMask', 'accessDaysMask', 'accessType', 'startDate', 'endDate', 'startTime', 'endTime', 'compareTime', 'result'])

    testCases = []
    testCases.append(testCase(keyMask=0xFF,
                             accessDaysMask=0xFF,
                             accessType=User.ACCESSTYPE_DAILY_ACCESS_PERIOD,
                             startDate=datetime.datetime(2003, 1, 1),
                             endDate=datetime.datetime(2008, 1, 1),
                             startTime=datetime.datetime(2003,1,1,hour=0, minute=0, second=1),
                             endTime=datetime.datetime(2008,1,1,hour=23, minute=59, second=59),
                             compareTime=datetime.datetime.now(),
                             result=False))
    testCases.append(testCase(keyMask=0xFF,
                             accessDaysMask=0xFF,
                             accessType=User.ACCESSTYPE_DAILY_ACCESS_PERIOD,
                             startDate=datetime.datetime(2003, 1, 1),
                             endDate=datetime.datetime(2018, 1, 1),
                             startTime=datetime.datetime(2003,1,1,hour=0, minute=0, second=1),
                             endTime=datetime.datetime(2008,1,1,hour=23, minute=59, second=59),
                             compareTime=datetime.datetime.now(),
                             result=False))
    testCases.append(testCase(keyMask=0xFF,
                              accessDaysMask=User.SATURDAY,
                              accessType=User.ACCESSTYPE_DAILY_ACCESS_PERIOD,
                              startDate=datetime.datetime(2003, 1, 1),
                              endDate=datetime.datetime(2016, 10, 15),
                              startTime=datetime.datetime(2003, 1, 1, hour=22, minute=10, second=1),
                              endTime=datetime.datetime(2008, 1, 1, hour=21, minute=59, second=59),
                              compareTime=datetime.datetime(2016,10,16,1,0,1),
                              result=False))
    iter= 0
    for test in testCases:
        testUser = User('Test', 'test', 'test', 'user', 0)

        print "testCase " + str(iter)
        print "\tcompared time \t= " + str(test.compareTime)
        print "\tkey  \t\t\t= " + str(test.keyMask)
        print "\tdays  \t\t\t= " + str(test.accessDaysMask)
        print "\tdate \t\t\t= " + str(test.startDate.date()) + " to " + str(test.endDate.date())
        print "\ttime \t\t\t= " + str(test.startTime.time()) + " to " + str(test.endTime.time())

        testUser.accessType = test.accessType
        testUser.keyMask = test.keyMask
        testUser.accessDaysMask = test.accessDaysMask
        testUser.accessDateStart = test.startDate
        testUser.accessDateEnd = test.endDate
        testUser.accessTimeStart = test.startTime
        testUser.accessTimeEnd = test.endTime

        print checkUserAccessPrivleges(test.compareTime, testUser)
        iter+=1