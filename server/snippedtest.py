__author__ = 'drobisch'
import datetime
import requests
req = requests.get('http://' + '192.168.2.108' + ':5000' + '/request/doorinfo')

