__author__ = 'drobisch'
import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits + string.lowercase):
    return ''.join(random.choice(chars) for _ in range(size))