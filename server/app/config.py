from configobj import ConfigObj
import os
import json

print os.path.dirname(os.path.abspath(__file__))

def conf_entry_to_bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def conf_entry_to_int(v):
    return int(v)

def gather_subsection(section, key):
    #if section.depth > 1:
    print "Subsection " + section.name , " ", section.depth

def config_lock():
    print "lock config"
    open("config.lock", 'a').close()

def config_is_locked():
    if os.path.isfile("config.lock"):
        return True
    else:
        return False

# global settings
WTF_CSRF_ENABLED = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# user defined settings from 'config.ini'
config = ConfigObj("config.ini")

NODE_LOCKED = config_is_locked()

# node settings
node_section = config['NODE']

NODE_NAME = node_section['NODE_NAME']
NODE_DOOR_AVAILABLE = conf_entry_to_bool(node_section['NODE_DOOR_AVAILABLE'])
if 'NODE_IS_MASTER' in node_section:
    NODE_IS_MASTER = conf_entry_to_bool(node_section['NODE_IS_MASTER'])
else:
    if 'NODE_MASTER' in  node_section:
        NODE_IS_MASTER = conf_entry_to_bool(node_section['NODE_MASTER'])


if NODE_IS_MASTER == True:
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

if 'SYNC_MASTER_DEFAULT_PASSWORD' in security_section:
    NODE_PASSWORD = security_section['SYNC_MASTER_DEFAULT_PASSWORD']
else:
    if 'NODE_PASSWORD' in security_section:
        NODE_PASSWORD = security_section['NODE_PASSWORD']


if 'DOOR' in config:
    door_section = config['DOOR']
    DOOR_OPENING_TIME = conf_entry_to_int(door_section['DOOR_OPENING_TIME'])
else:
    DOOR_OPENING_TIME = 16

# extension settings
if 'EXTENSION' in config:
    extension_section = config['EXTENSION']
    EXTENSION_NAME = extension_section['EXTENSION_NAME']
    EXTENSION_FRONTEND_DISABLE = conf_entry_to_bool(extension_section['EXTENSION_FRONTEND_DISABLE'])
else:
    if NODE_LOCKED is True:
        if NODE_IS_MASTER is True:
            EXTENSION_NAME = 'master'
            EXTENSION_FRONTEND_DISABLE = False
        else:
            EXTENSION_NAME = 'setup'
            EXTENSION_FRONTEND_DISABLE = False
    else:
        EXTENSION_NAME = 'setup'
        EXTENSION_FRONTEND_DISABLE = False

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
if NODE_IS_MASTER == True:
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

def getConfigJSON():
    config_json_root = {}

    config_json_master = {}

    config_json_master["entries"] = []
    config_json_master["entries"].append({"name": "RFID_GLOBAL_PASSWORD", "displayName": "Global RFID password", "descryption" : "The system-wide RFID-password. IMPROTANT: Please remember this key. Use the key for all slaves in the same system!", "value": RFID_GLOBAL_PASSWORD})
    config_json_master["entries"].append({"name": "NODE_IS_MASTER", "displayName": "Is master-node", "descryption" : "Is the node the master-node.", "value": NODE_IS_MASTER})
    config_json_master["entries"].append({"name": "STATISTICS_ENABLE", "displayName": "Enable statistics", "descryption" : "Enable the statistic module.", "value": STATISTICS_ENABLE})
    config_json_master["entries"].append({"name": "CLEANUP_EANBLE", "displayName": "Enable log-cleanup", "descryption" : "Enable cleanup of the log (and free database-size).", "value": CLEANUP_EANBLE})
    config_json_master["entries"].append({"name": "CLEANUP_THRESHOLD", "displayName": "Logging threshold", "descryption" : "If cleanup is enabled specify how many days the log should be stored.", "value": CLEANUP_THRESHOLD})
    config_json_master["entries"].append({"name": "NODE_SYNC_CYCLIC", "displayName": "Cyclic synchronisation", "descryption" : "Enable cyclic synchronisation. If enabled, synch. start every X minutes (based on synch. cycle). If disabled synchronisation starts every day.", "value": NODE_SYNC_CYCLIC})
    config_json_master["entries"].append({"name": "NODE_SYNC_CYCLE", "displayName": "Synchronisation cycle", "descryption" : "Time in minutes after new synchronisation starts (if cyclic synhronisation is enabled).", "value": NODE_SYNC_CYCLE})
    config_json_master["entries"].append({"name": "NODE_SYNC_ON_STARTUP", "displayName": "Synch. on startup", "descryption" : "Force synchronisation on startup of the system.", "value": NODE_SYNC_ON_STARTUP})

    config_json_node = {}
    config_json_node["entries"] = []
    config_json_node["entries"].append({"name": "NODE_NAME", "displayName": "Name", "descryption" : "The name of the node", "value": NODE_NAME})
    config_json_node["entries"].append({"name": "NODE_PASSWORD", "displayName": "Password", "descryption" : "Password used for the admin-account (master) or synchronisation (slave).", "value": NODE_PASSWORD})
    config_json_node["entries"].append({"name": "EXTENSION_NAME", "displayName": "Extension", "descryption" : "The extension describe the functionality (logic) and user-interface (frontend).", "value": EXTENSION_NAME})
    config_json_node["entries"].append({"name": "EXTENSION_FRONTEND_DISABLE", "displayName": "Extension UI disable", "descryption" : "Disable the user-interface (frontend) of the extension.", "value": EXTENSION_FRONTEND_DISABLE})
    config_json_node["entries"].append({"name": "DEBUG", "displayName": "Enable debug info.", "descryption" : "Enable flask debug informations.", "value": DEBUG})

    config_json_interfaces = {}
    config_json_interfaces["entries"] = []
    config_json_interfaces["entries"].append({"name": "NODE_DOOR_AVAILABLE", "displayName": "Door connected", "descryption" : "The node interface a door?", "value": NODE_DOOR_AVAILABLE})
    config_json_interfaces["entries"].append({"name": "DOOR_OPENING_TIME", "displayName": "Door opening duration", "descryption" : "The duration the door keep open after request.", "value": DOOR_OPENING_TIME })

    config_json_advanced = {}
    config_json_advanced["entries"] = []
    config_json_advanced["entries"].append({"name": "MAIL_SERVER", "displayName": "Mail server", "descryption" : "Mail-server address.", "value": MAIL_SERVER})
    config_json_advanced["entries"].append({"name": "MAIL_PORT", "displayName": "Mail server port", "descryption" : "Mail-server port.", "value": MAIL_PORT})
    config_json_advanced["entries"].append({"name": "MAIL_USE_TLS", "displayName": "Mail use TLS", "descryption" : "Do the mail server use TLS.", "value": MAIL_USE_TLS})
    config_json_advanced["entries"].append({"name": "MAIL_USE_SSL", "displayName": "Mail use SSL", "descryption" : "Do the mail server use SSL.", "value": MAIL_USE_SSL})
    config_json_advanced["entries"].append({"name": "MAIL_USERNAME", "displayName": "Mail userneame", "descryption" : "The username to login to the mail-server.", "value": MAIL_USERNAME})
    config_json_advanced["entries"].append({"name": "MAIL_PASSWORD", "displayName": "Mail password", "descryption" : "The password to login to the mail-server.", "value": MAIL_PASSWORD})


    config_json_root["lock"] = config_is_locked()
    config_json_root["master_config"] = config_json_master
    config_json_root["node_config"] = config_json_node
    config_json_root["interface_config"] = config_json_interfaces
    config_json_root["advanced_config"] = config_json_advanced
    return config_json_root


#config_lock()
#config.walk(gather_subsection)

#for section in config.sections:
#    print section

print json.dumps(getConfigJSON(), indent=2)
