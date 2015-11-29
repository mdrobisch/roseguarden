from configobj import ConfigObj
import os
print os.path.dirname(os.path.abspath(__file__))


def conf_entry_to_bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def conf_entry_to_int(v):
  return int(v)



config = ConfigObj("config.ini")
print str(config)

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

rfid_section = config['RFID']
RFID_GLOBAL_PASSWORD = rfid_section['RFID_GLOBAL_PASSWORD']
