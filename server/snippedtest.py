__author__ = 'drobisch'
import datetime
import requests
import random
import os
import marshmallow
import base64
import time

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

weekday_test()
