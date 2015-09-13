__author__ = 'drobisch'
import datetime

d = (datetime.datetime.today()).replace(hour=0,minute=0,second=0,microsecond=0)
d2 = (datetime.datetime.today() + datetime.timedelta(365*15)).replace(hour=23,minute=59,second=0,microsecond=0)

print d, d2
