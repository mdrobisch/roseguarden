import imp
import os
from config import NODE_LOCKED, EXTENSION_NAME

if NODE_LOCKED is False:
    extension_name = "setup"
else:
    extension_name = EXTENSION_NAME

extension = imp.load_source('module', 'extensions/' + extension_name + '/extension.py')

extension.extension_event_loading()

if not hasattr(extension, "CONFIG_DISABLE_UPDATE_USER"):
    extension.CONFIG_DISABLE_UPDATE_USER = False
    print "  .. use default config for CONFIG_DISABLE_SYNC_CYCLES ", extension.CONFIG_DISABLE_UPDATE_USER

if not hasattr(extension, "CONFIG_DISABLE_SYNC_CYCLES"):
    extension.CONFIG_DISABLE_SYNC_CYCLES = False
    print "  .. use default config for CONFIG_DISABLE_SYNC_CYCLES ", extension.CONFIG_DISABLE_SYNC_CYCLES

if not hasattr(extension, "CONFIG_DISABLE_CLEANUP_CYLCES"):
    extension.CONFIG_DISABLE_CLEANUP_CYLCES = False
    print "  .. use default config for CONFIG_DISABLE_CLEANUP_CYLCES ", extension.CONFIG_DISABLE_CLEANUP_CYLCES