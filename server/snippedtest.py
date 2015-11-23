__author__ = 'drobisch'
import datetime
import requests
import random
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

random_test()