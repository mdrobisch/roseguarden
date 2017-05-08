import imp
import os
from config import ConfigManager

class ExtensionManagerClass(object):

    def __init__(self):
        self.loadExtension()

    def reloadExtension(self):
        self.loadExtension()

    def loadExtension(self):
        if ConfigManager.NODE_LOCKED is False:
            self.extension_name = "setup"
        else:
            self.extension_name = ConfigManager.EXTENSION_NAME

        if ConfigManager.NODE_LOCKED is False:
            self.extension_name = "setup"
        else:
            self.extension_name = ConfigManager.EXTENSION_NAME

        self.extension = imp.load_source('module', 'extensions/' + self.extension_name + '/extension.py')

        self.extension.extension_event_loading()

        if not hasattr(self.extension, "CONFIG_DISABLE_UPDATE_USER"):
            self.extension.CONFIG_DISABLE_UPDATE_USER = False
            print "  .. use default config for CONFIG_DISABLE_SYNC_CYCLES ", self.extension.CONFIG_DISABLE_UPDATE_USER

        if not hasattr(self.extension, "CONFIG_DISABLE_SYNC_CYCLES"):
            self.extension.CONFIG_DISABLE_SYNC_CYCLES = False
            print "  .. use default config for CONFIG_DISABLE_SYNC_CYCLES ", self.extension.CONFIG_DISABLE_SYNC_CYCLES

        if not hasattr(self.extension, "CONFIG_DISABLE_CLEANUP_CYLCES"):
            self.extension.CONFIG_DISABLE_CLEANUP_CYLCES = False
            print "  .. use default config for CONFIG_DISABLE_CLEANUP_CYLCES ", self.extension.CONFIG_DISABLE_CLEANUP_CYLCES

ExtensionManager = ExtensionManagerClass()
