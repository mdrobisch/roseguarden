from configobj import ConfigObj
import os
import json

print os.path.dirname(os.path.abspath(__file__))


def conf_entry_to_bool(v):
    return v  # v.lower() in ("yes", "true", "t", "1")


def conf_entry_to_int(v):
    return int(v)


def gather_subsection(section, key):
    # if section.depth > 1:
    print "Subsection " + section.name, " ", section.depth


def config_lock():
    print "lock config"
    open("config.lock", 'a').close()


def config_is_locked():
    if os.path.isfile("config.lock"):
        return True
    else:
        return False


class ConfigManagerClass(object):

    # global settings
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self):
        self.loadConfig()

    def reloadConfig(self):
        self.loadConfig()

    def loadConfig(self):
        # user defined settings from 'config.ini'
        self.config = ConfigObj("config.ini", unrepr=True) # indent_type='   '

        self.NODE_LOCKED = config_is_locked()

        # node settings
        node_section = self.config['NODE']

        self.NODE_NAME = node_section['NODE_NAME']
        self.NODE_DOOR_AVAILABLE = conf_entry_to_bool(node_section['NODE_DOOR_AVAILABLE'])
        if 'NODE_IS_MASTER' in node_section:
            self.NODE_IS_MASTER = conf_entry_to_bool(node_section['NODE_IS_MASTER'])
        else:
            if 'NODE_MASTER' in  node_section:
                self.NODE_IS_MASTER = conf_entry_to_bool(node_section['NODE_MASTER'])


        if self.NODE_IS_MASTER == True:
            self.NODE_SYNC_CYCLIC = conf_entry_to_bool(node_section['NODE_SYNC_CYCLIC'])
            self.NODE_SYNC_CYCLE = conf_entry_to_int(node_section['NODE_SYNC_CYCLE'])
            self.NODE_SYNC_ON_STARTUP = conf_entry_to_bool(node_section['NODE_SYNC_ON_STARTUP'])
        else:
            self.NODE_SYNC_CYCLIC = False
            self.NODE_SYNC_ON_STARTUP = False
            self.NODE_SYNC_CYCLE = 9000

        try:
            self.NODE_LOG_MERGE = conf_entry_to_int(node_section['NODE_LOG_MERGE'])
        except KeyError:
            print "Missing config NODE_LOG_MERGE in config.ini: set NODE_LOG_MERGE to 10 minutes"
            self.NODE_LOG_MERGE = 10

        try:
            statistics_section = self.config['STATISTICS']
            try:
                self.STATISTICS_ENABLE = conf_entry_to_bool(statistics_section['STATISTICS_ENABLE'])
            except KeyError:
                print "Missing config STATISTICS_ENABLE in config.ini: set STATISTICS_ENABLE to false"
                self.STATISTICS_ENABLE = False
        except KeyError:
            print "Missing config STATISTICS section in config.ini:"
            print "     Set STATISTICS_ENABLE to false"
            self.STATISTICS_ENABLE = False

        # flask settings
        flask_section = self.config['FLASK']
        self.DEBUG = conf_entry_to_bool(flask_section['DEBUG'])

        # security settings
        security_section = self.config['SECURITY']
        self.RFID_GLOBAL_PASSWORD = security_section['RFID_GLOBAL_PASSWORD']

        if 'SYNC_MASTER_DEFAULT_PASSWORD' in security_section:
            self.INITIAL_NODE_PASSWORD = security_section['SYNC_MASTER_DEFAULT_PASSWORD']
        else:
            if 'INITIAL_NODE_PASSWORD' in security_section:
                self.INITIAL_NODE_PASSWORD = security_section['INITIAL_NODE_PASSWORD']
            else:
                self.INITIAL_NODE_PASSWORD = ""

        if 'DOOR' in self.config:
            door_section = self.config['DOOR']
            self.DOOR_OPENING_TIME = conf_entry_to_int(door_section['DOOR_OPENING_TIME'])
            if('DOOR_KEYMASK' in door_section):
                self.DOOR_KEYMASK = conf_entry_to_int(door_section['DOOR_KEYMASK'])
            else:
                self.DOOR_KEYMASK = 0

        else:
            self.DOOR_OPENING_TIME = 16
            self.DOOR_KEYMASK = 0

        # extension settings
        if 'EXTENSION' in self.config:
            extension_section = self.config['EXTENSION']
            self.EXTENSION_NAME = extension_section['EXTENSION_NAME']
            self.EXTENSION_FRONTEND_DISABLE = conf_entry_to_bool(extension_section['EXTENSION_FRONTEND_DISABLE'])
        else:
            self.config['EXTENSION'] = {}
            self.config['EXTENSION']['EXTENSION_NAME'] = u'setup'
            self.config['EXTENSION']['EXTENSION_FRONTEND_DISABLE'] = False
            self.config.comments['EXTENSION'].append("")
            if self.NODE_LOCKED is True:
                if self.NODE_IS_MASTER is True:
                    self.EXTENSION_NAME = 'master'
                    self.EXTENSION_FRONTEND_DISABLE = False
                else:
                    self.EXTENSION_NAME = 'setup'
                    self.EXTENSION_FRONTEND_DISABLE = False
            else:
                self.EXTENSION_NAME = 'setup'
                self.EXTENSION_FRONTEND_DISABLE = False

        # backup settings

        backup_section = self.config['BACKUP']
        self.BACKUP_ENABLE_FTP = conf_entry_to_bool(backup_section['BACKUP_ENABLE_FTP'])

        if self.BACKUP_ENABLE_FTP == True:
            self.ALCHEMYDUMPS_FTP_SERVER = backup_section['BACKUP_FTP_SERVER']
            self.ALCHEMYDUMPS_FTP_USER = backup_section['BACKUP_FTP_USER']
            self.ALCHEMYDUMPS_FTP_PASSWORD = backup_section['BACKUP_FTP_PASSWORD']
            self.ALCHEMYDUMPS_FTP_PATH = backup_section['BACKUP_FTP_PATH']
        else:
            self.ALCHEMYDUMPS_FTP_SERVER = ''
            self.ALCHEMYDUMPS_FTP_USER = ''
            self.ALCHEMYDUMPS_FTP_PASSWORD = ''
            self.ALCHEMYDUMPS_FTP_PATH = ''

        cleanup_section = self.config['CLEANUP']

        self.CLEANUP_EANBLE = conf_entry_to_bool(cleanup_section['CLEANUP_EANBLE'])

        if self.CLEANUP_EANBLE == True:
            self.CLEANUP_THRESHOLD = conf_entry_to_int(cleanup_section['CLEANUP_THRESHOLD'])
        else:
            self.CLEANUP_THRESHOLD = 1000

        # settings for flask-mail, if available
        if self.NODE_IS_MASTER == True:
            mail_section = self.config['MAIL']
            self.MAIL_SERVER = mail_section['MAIL_SERVER']
            self.MAIL_PORT = conf_entry_to_int(mail_section['MAIL_PORT'])
            self.MAIL_USE_TLS = conf_entry_to_bool(mail_section['MAIL_USE_TLS'])
            self.MAIL_USE_SSL = conf_entry_to_bool(mail_section['MAIL_USE_SSL'])
            self.MAIL_USERNAME = mail_section['MAIL_USERNAME']
            self.MAIL_PASSWORD = mail_section['MAIL_PASSWORD']
        else:
            self.MAIL_SERVER = ''
            self.MAIL_PORT = 465
            self.MAIL_USE_TLS = False
            self.MAIL_USE_SSL = True
            self.MAIL_USERNAME = ''
            self.MAIL_PASSWORD = ''

    def locateJsonEntryByName(self,e,name):
        if e.get('name',None) == name:
            return e

        for child in e.get('children',[]):
            result = self.locateJsonEntryByName(child,name)
            if result is not None:
                return result
        return None

    def updateEntries(self,configDict):
        for child in configDict:
            if isinstance(configDict, (dict)):
                if isinstance(configDict[child],(list,dict)):
                    self.updateEntries(configDict[child])
                else:
                    if child == 'name':
                        if hasattr(self,configDict[child]) and 'value' in configDict:
                            setattr(self,configDict[child], configDict['value'])
                            for section_name in self.config.sections:
                                section = self.config[section_name]
                                if configDict[child] in section:
                                    section[configDict[child]] = configDict['value']
                                    print configDict[child], " ", configDict['value'], " changed"

                        else:
                            if 'value' in configDict:
                                print configDict[child], " ", configDict['value'], " unchanged"
            else:
                if isinstance(child,(dict)):
                    self.updateEntries(child)

    def updateConfigByJSON(self,configJSON):
        self.updateEntries(configJSON)
        print self.config['NODE']['NODE_NAME']
        self.config.filename = 'config.ini'
        self.config.write()
        return 0

    def getConfigJSON(self):
        config_json_root = {}

        config_json_master = {}

        config_json_master["entries"] = []
        config_json_master["entries"].append({"name": "RFID_GLOBAL_PASSWORD", "displayName": "Global RFID password", "descryption" : "The system-wide RFID-password. IMPROTANT: Please remember this key. Use the key for all slaves in your system!", "value": self.RFID_GLOBAL_PASSWORD})
        config_json_master["entries"].append({"name": "NODE_IS_MASTER", "displayName": "Is master-node", "descryption" : "Is the node the master-node.", "value": self.NODE_IS_MASTER})
        config_json_master["entries"].append({"name": "STATISTICS_ENABLE", "displayName": "Enable statistics", "descryption" : "Enable the statistic module.", "value": self.STATISTICS_ENABLE})
        config_json_master["entries"].append({"name": "CLEANUP_EANBLE", "displayName": "Enable log-cleanup", "descryption" : "Enable cleanup of the log (and free database-size).", "value": self.CLEANUP_EANBLE})
        config_json_master["entries"].append({"name": "CLEANUP_THRESHOLD", "displayName": "Logging threshold", "descryption" : "If cleanup is enabled specify how many days the log should be stored.", "value": self.CLEANUP_THRESHOLD})
        config_json_master["entries"].append({"name": "NODE_SYNC_CYCLIC", "displayName": "Cyclic synchronisation", "descryption" : "Enable cyclic synchronisation. If enabled, synch. start every X minutes (based on synch. cycle). If disabled synchronisation starts every day.", "value": self.NODE_SYNC_CYCLIC})
        config_json_master["entries"].append({"name": "NODE_SYNC_CYCLE", "displayName": "Synchronisation cycle", "descryption" : "Time in minutes after new synchronisation starts (if cyclic synhronisation is enabled).", "value": self.NODE_SYNC_CYCLE})
        config_json_master["entries"].append({"name": "NODE_SYNC_ON_STARTUP", "displayName": "Synch. on startup", "descryption" : "Force synchronisation on startup of the system.", "value": self.NODE_SYNC_ON_STARTUP})

        config_json_node = {}
        config_json_node["entries"] = []
        config_json_node["entries"].append({"name": "NODE_NAME", "displayName": "Name", "descryption" : "The name of the node", "value": self.NODE_NAME})
        config_json_node["entries"].append({"name": "INITIAL_NODE_PASSWORD", "displayName": "Password", "descryption" : "Password used to setup the admin-account (master) or synchronisation (slave). It is used only for setup and can be changed afterwards.", "value": ""})
        config_json_node["entries"].append({"name": "EXTENSION_NAME", "displayName": "Extension", "descryption" : "The extension describe the functionality (logic) and user-interface (frontend).", "value": self.EXTENSION_NAME})
        config_json_node["entries"].append({"name": "EXTENSION_FRONTEND_DISABLE", "displayName": "Extension UI disable", "descryption" : "Disable the user-interface (frontend) of the extension.", "value": self.EXTENSION_FRONTEND_DISABLE})
        config_json_node["entries"].append({"name": "DEBUG", "displayName": "Enable debug info.", "descryption" : "Enable flask debug informations.", "value": self.DEBUG})

        config_json_interfaces = {}
        config_json_interfaces["entries"] = []
        config_json_interfaces["entries"].append({"name": "NODE_DOOR_AVAILABLE", "displayName": "Door connected", "descryption" : "The node interface a door?", "value": self.NODE_DOOR_AVAILABLE})
        config_json_interfaces["entries"].append({"name": "DOOR_KEYMASK", "displayName": "Door key mask", "descryption" : "Door keymask. Authorize the given keys to open the door.", "value": self.DOOR_KEYMASK })
        config_json_interfaces["entries"].append({"name": "DOOR_OPENING_TIME", "displayName": "Door opening duration", "descryption" : "The duration the door keep open after request.", "value": self.DOOR_OPENING_TIME })

        config_json_advanced = {}
        config_json_advanced["entries"] = []
        config_json_advanced["entries"].append({"name": "MAIL_SERVER", "displayName": "Mail server", "descryption" : "Mail-server address.", "value": self.MAIL_SERVER})
        config_json_advanced["entries"].append({"name": "MAIL_PORT", "displayName": "Mail server port", "descryption" : "Mail-server port.", "value": self.MAIL_PORT})
        config_json_advanced["entries"].append({"name": "MAIL_USE_TLS", "displayName": "Mail use TLS", "descryption" : "Do the mail server use TLS.", "value": self.MAIL_USE_TLS})
        config_json_advanced["entries"].append({"name": "MAIL_USE_SSL", "displayName": "Mail use SSL", "descryption" : "Do the mail server use SSL.", "value": self.MAIL_USE_SSL})
        config_json_advanced["entries"].append({"name": "MAIL_USERNAME", "displayName": "Mail userneame", "descryption" : "The username to login to the mail-server.", "value": self.MAIL_USERNAME})
        config_json_advanced["entries"].append({"name": "MAIL_PASSWORD", "displayName": "Mail password", "descryption" : "The password to login to the mail-server.", "value": self.MAIL_PASSWORD})

        config_json_root["lock"] = config_is_locked()
        config_json_root["master_config"] = config_json_master
        config_json_root["node_config"] = config_json_node
        config_json_root["interface_config"] = config_json_interfaces
        config_json_root["advanced_config"] = config_json_advanced
        return config_json_root

ConfigManager = ConfigManagerClass()