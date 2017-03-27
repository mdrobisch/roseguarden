import imp
import os

extension_name = "setup"
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