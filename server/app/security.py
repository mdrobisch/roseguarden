__author__ = 'drobisch'
import string
import random
import datetime
import settings
from models import User

def generator_password(size=6, chars=string.ascii_uppercase + string.digits + string.lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

def checkUserAccessPrivleges(user):
    # check for invalid accessType == no access
    if (user.keyMask & settings.SETTING_NODE_VALID_KEYS_MASK) == 0:
        return 'Denied access because of unauthorized keys.'

    if user.accessType == user.ACCESSTYPE_NO_ACCESS or user.accessType > user.ACCESSTYPE_MAX:
        return 'Denied access because of unauthorized access type.'

    # check start-date and end-date for accessType == period
    if user.accessType == user.ACCESSTYPE_ACCESS_PERIOD:
        if user.accessDateStart > datetime.datetime.now():
            return 'Denied access because of invalid start of period.'
        if user.accessDateEnd < datetime.datetime.now():
            return 'Denied access because of invalid end of period.'
    # check day counter for accessType == day-budget
    if user.accessType == user.ACCESSTYPE_ACCESS_DAYS:
        if user.accessDayCounter <= 0:
            return 'Denied access because of insufficient day-budget.'
    if (int(1 << datetime.datetime.now().weekday()) & user.accessDaysMask) == 0:
        return 'Denied access because of invalid access weekday.'
    if user.accessTimeStart.time() > datetime.datetime.now().time():
        return 'Denied access because of invalid day-time start.'
    if user.accessTimeEnd.time() < datetime.datetime.now().time():
        return 'Denied access because of invalid day-time end.'
    return "Access granted."