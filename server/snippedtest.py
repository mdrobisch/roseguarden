__author__ = 'drobisch'
import datetime
import requests
import random
import os
import marshmallow
import base64
import time
import Queue
from collections import namedtuple

#req = requests.get('http://' + '192.168.2.108' + ':5000' + '/request/doorinfo')

def random_test():
    for i in range(0,50):
        print random.randrange(0, 3)


def hex_string_conversion_test():
    key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
    key2 = []
    key3 = []
    hexstr = ""
    print key

    for i in range(0,6):
        num = random.randrange(0, 256)
        hexstr = hexstr + format(num, '02X') + ' '
        key2.append(num)
    print key2

    print hexstr

    print hexstr.split()

    for x in hexstr.split():
        key3.append(int(x, 16))

    print key3

def spilt_string_conversion():
    newkey = []
    newkeystring = '45-39-68-A7-F1-B5'
    print newkeystring
    print newkeystring.split('-')
    for x in newkeystring.split('-'):
        newkey.append(int(x, 16))
    print newkey

def random_secret():
    key2 = []
    hexstr = ''
    for i in range(0,6):
        if i != 0:
            hexstr = hexstr + '-'
        num = random.randrange(0, 256)
        hexstr = hexstr + format(num, '02X')
    print '(' + hexstr + ')'


def daily_worker_test():
    lasttime = datetime.datetime.now()
    now = datetime.datetime.now()
    while 1:
        compare_time = lasttime.replace(hour=4, minute=0, second=0, microsecond=0)
        if compare_time > lasttime:
            next_time = compare_time
        else:
            next_time = compare_time + datetime.timedelta(days=1)
        #print 'next time: ' + str(next_time)
        print 'raffed time: ' + str(now)
        if(now > next_time):
            print '    doing something'
            lasttime = now
        now += datetime.timedelta(hours=1.5)
        time.sleep(0.5)
    print next_time

def datetime_tz_test():
    dt_str = '2015-12-12T00:00:00+00:00'
    result =  marshmallow.utils.from_iso (dt_str)
    print result
    #print time.strftime('%Y-%m-%dT%H:%M:%S')

    #datetime.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S%Z')

def weekday_test():
    print str((datetime.datetime.now() - datetime.timedelta(2)).year)

def environ_test():
    #os.environ['ROSEGUARDEN_GLOBAL_RFID_PASSWORD'] = str("Test")
    print os.environ.get('ROSEGUARDEN_GLOBAL_RFID_PASSWORD')


def thresholdTest():
    userData = [0,0,0,2,2,1,4,5,2,3,4,8,13,1,10,99,9]
    userDataLowAction = []
    userDataMediumAction = []
    userDataHighAction = []
    userData.append(22)
    userData.sort()

    noActionUsers = 0
    actionUsers = 0

    lowThresholdIndex = 0
    highThresholdIndex = 0

    lowThreshold = 0
    highThreshold = 0

    for i in range(0, len(userData)):
        print i
        if userData[i] == 0:
            noActionUsers += 1
        else:
            actionUsers = len(userData)
            mediumThresholdIndex = noActionUsers + int(round((actionUsers - noActionUsers) * 0.5, 0))
            if i > mediumThresholdIndex:
                highThreshold += userData[i]
            else:
                lowThreshold += userData[i]

    highThreshold = highThreshold / ((actionUsers - noActionUsers) * 0.5)
    lowThreshold  = lowThreshold / ((actionUsers - noActionUsers) * 0.5)

    lowActionUserAccesses = 0
    mediumActionUserAccesses = 0
    highActionUserAccesses = 0

    for i in range(noActionUsers, len(userData)):
        if userData[i] < lowThreshold:
            userDataLowAction.append(userData[i])
            lowActionUserAccesses += userData[i]
        else:
            if userData[i] < highThreshold:
                userDataMediumAction.append(userData[i])
                mediumActionUserAccesses += userData[i]
            else:
                userDataHighAction.append(userData[i])
                highActionUserAccesses += userData[i]

    print userData
    print noActionUsers
    print mediumThresholdIndex
    print lowThreshold
    print highThreshold
    print str(lowActionUserAccesses) + " " + str(round(float(lowActionUserAccesses) / len(userDataLowAction),1)) + " " + str(userDataLowAction)
    print str(mediumActionUserAccesses) + " " + str(round(float(mediumActionUserAccesses) / len(userDataMediumAction),1)) + " " + str(userDataMediumAction)
    print str(highActionUserAccesses) + " " + str(round(float(highActionUserAccesses) / len(userDataHighAction),1)) + " " + str(userDataHighAction)
    #weekday_test()

QueueData = namedtuple('QueueData', ['x', 'y'])

qu = Queue.Queue()
qu.put(QueueData(x=1, y=2))
print qu.qsize()