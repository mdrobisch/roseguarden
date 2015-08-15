__author__ = 'drobisch'
import os

def test_envirment():
    try:
        os.environ["MAIL_USERNAME"]
    except KeyError:
        print 'MAIL_USERNAME missing. Please add enviroment variable.'
    try:
        os.environ["MAIL_PASSWORD"]
    except KeyError:
        print 'MAIL_PASSWORD missing. Please add enviroment variable.'
