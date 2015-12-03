from configobj import ConfigObj
import os
print os.path.dirname(os.path.abspath(__file__))


def conf_entry_to_bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def conf_entry_to_int(v):
    return int(v)



config = ConfigObj("config.ini")

node_section = config['NODE']
NODE_NAME = node_section['NODE_NAME']

flask_section = config['FLASK']
DEBUG = conf_entry_to_bool(flask_section['DEBUG'])
WTF_CSRF_ENABLED = conf_entry_to_bool(flask_section['WTF_CSRF_ENABLED'])

mail_section = config['MAIL']
MAIL_SERVER = mail_section['MAIL_SERVER']
MAIL_PORT = conf_entry_to_int(mail_section['MAIL_PORT'])
MAIL_USE_TLS = conf_entry_to_bool(mail_section['MAIL_USE_TLS'])
MAIL_USE_SSL = conf_entry_to_bool(mail_section['MAIL_USE_SSL'])
MAIL_USERNAME = mail_section['MAIL_USERNAME']
MAIL_PASSWORD = mail_section['MAIL_PASSWORD']

security_section = config['SECURITY']
RFID_GLOBAL_PASSWORD = security_section['RFID_GLOBAL_PASSWORD']
SYNC_MASTER_DEFAULT_PASSWORD = security_section['SYNC_MASTER_DEFAULT_PASSWORD']
