__author__ = 'drobisch'
import os

MAIL_USERNAME = os.environ.get('ROSEGUARDEN_MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('ROSEGUARDEN_MAIL_PASSWORD')

RFID_GLOBAL_PASSWORD = os.environ.get('ROSEGUARDEN_GLOBAL_RFID_PASSWORD')


def test_envirment():
    try:
        os.environ["ROSEGUARDEN_MAIL_USERNAME"]
    except KeyError:
        print 'ROSEGUARDEN_MAIL_USERNAME missing. Please add enviroment variable.'
    try:
        os.environ["ROSEGUARDEN_MAIL_PASSWORD"]
    except KeyError:
        print 'ROSEGUARDEN_MAIL_PASSWORD missing. Please add enviroment variable.'
    try:
        os.environ["ROSEGUARDEN_GLOBAL_RFID_PASSWORD"]
    except KeyError:
        print 'ROSEGUARDEN_GLOBAL_RFID_PASSWORD missing. Please add enviroment variable.'
