from configobj import ConfigObj
import os
print os.path.dirname(os.path.abspath(__file__))


def conf_entry_to_bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def conf_entry_to_int(v):
    return int(v)

# global settings
WTF_CSRF_ENABLED = False

# user defined settings from 'config.ini'
config = ConfigObj("config.ini")

# node settings
node_section = config['NODE']
NODE_NAME = node_section['NODE_NAME']
NODE_MASTER = conf_entry_to_bool(node_section['NODE_MASTER'])
NODE_DOOR_AVAILABLE = conf_entry_to_bool(node_section['NODE_DOOR_AVAILABLE'])

if NODE_MASTER == True:
    NODE_SYNC_CYCLIC = conf_entry_to_bool(node_section['NODE_SYNC_CYCLIC'])
    NODE_SYNC_CYCLE = conf_entry_to_int(node_section['NODE_SYNC_CYCLE'])
    NODE_SYNC_ON_STARTUP = conf_entry_to_bool(node_section['NODE_SYNC_ON_STARTUP'])
else:
    NODE_SYNC_CYCLIC = False
    NODE_SYNC_ON_STARTUP = False
    NODE_SYNC_CYCLE = 9000

try:
    NODE_LOG_MERGE = conf_entry_to_int(node_section['NODE_LOG_MERGE'])
except KeyError:
    print "Missing config NODE_LOG_MERGE in config.ini: set NODE_LOG_MERGE to 10 minutes"
    NODE_LOG_MERGE = 10

try:
    statistics_section = config['STATISTICS']
    try:
        STATISTICS_ENABLE = conf_entry_to_bool(statistics_section['STATISTICS_ENABLE'])
    except KeyError:
        print "Missing config STATISTICS_ENABLE in config.ini: set STATISTICS_ENABLE to false"
        STATISTICS_ENABLE = False
except KeyError:
    print "Missing config STATISTICS section in config.ini:"
    print "     Set STATISTICS_ENABLE to false"
    STATISTICS_ENABLE = False


# flask settings
flask_section = config['FLASK']
DEBUG = conf_entry_to_bool(flask_section['DEBUG'])

# security settings
security_section = config['SECURITY']
RFID_GLOBAL_PASSWORD = security_section['RFID_GLOBAL_PASSWORD']
SYNC_MASTER_DEFAULT_PASSWORD = security_section['SYNC_MASTER_DEFAULT_PASSWORD']

# backup settings

backup_section = config['BACKUP']
BACKUP_ENABLE_FTP = conf_entry_to_bool(backup_section['BACKUP_ENABLE_FTP'])

if BACKUP_ENABLE_FTP == True:
    ALCHEMYDUMPS_FTP_SERVER = backup_section['BACKUP_FTP_SERVER']
    ALCHEMYDUMPS_FTP_USER = backup_section['BACKUP_FTP_USER']
    ALCHEMYDUMPS_FTP_PASSWORD = backup_section['BACKUP_FTP_PASSWORD']
    ALCHEMYDUMPS_FTP_PATH = backup_section['BACKUP_FTP_PATH']
else:
    ALCHEMYDUMPS_FTP_SERVER = ''
    ALCHEMYDUMPS_FTP_USER = ''
    ALCHEMYDUMPS_FTP_PASSWORD = ''
    ALCHEMYDUMPS_FTP_PATH = ''

cleanup_section = config['CLEANUP']

CLEANUP_EANBLE = conf_entry_to_bool(cleanup_section['CLEANUP_EANBLE'])

if CLEANUP_EANBLE == True:
    CLEANUP_THRESHOLD = conf_entry_to_int(cleanup_section['CLEANUP_THRESHOLD'])
else:
    CLEANUP_THRESHOLD = 1000

# settings for flask-mail, if available
if NODE_MASTER == True:
    mail_section = config['MAIL']
    MAIL_SERVER = mail_section['MAIL_SERVER']
    MAIL_PORT = conf_entry_to_int(mail_section['MAIL_PORT'])
    MAIL_USE_TLS = conf_entry_to_bool(mail_section['MAIL_USE_TLS'])
    MAIL_USE_SSL = conf_entry_to_bool(mail_section['MAIL_USE_SSL'])
    MAIL_USERNAME = mail_section['MAIL_USERNAME']
    MAIL_PASSWORD = mail_section['MAIL_PASSWORD']
else:
    MAIL_SERVER = ''
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
