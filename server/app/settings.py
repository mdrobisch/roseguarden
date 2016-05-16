__author__ = 'drobisch'

from models import Setting
from server import db

def setting_value_to_bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def setting_value_to_int(v):
    return int(v)

def setting_value_to_float(v):
    return float(v)


def getSettingValue(name, type, default):
    setting = Setting.query.filter(Setting.name == name).first()
    if setting == None:
        print "generate setting " + str(name) + " with default = " +  str(default)
        setOrUpdateSettingValue(name,type,default)
        return default
    else:
        if setting.type == Setting.SETTINGTYPE_STRING:
            return setting.value

        if setting.type == Setting.SETTINGTYPE_BOOL:
            return setting_value_to_bool(setting.value)

        if setting.type == Setting.SETTINGTYPE_FLOAT:
            return setting_value_to_float(setting.value)

        if setting.type == Setting.SETTINGTYPE_INT:
            return setting_value_to_int(setting.value)
        return default

def setOrUpdateSettingValue(name, type, value):
    setting = Setting.query.filter(Setting.name == name).first()
    if setting == None:
        newSetting = Setting(name, value, type)
        db.session.add(newSetting)
    else:
        setting.value = str(value)
        setting.type = int(type)
    db.session.commit()
    updateSettingFromDatabase()

def updateSettingFromDatabase():
    global SETTING_NODE_VALID_KEYS_MASK
    SETTING_NODE_VALID_KEYS_MASK = getSettingValue("NODE_VALID_KEYS_MASK", Setting.SETTINGTYPE_INT, 0)


try:
    SETTING_NODE_VALID_KEYS_MASK = getSettingValue("NODE_VALID_KEYS_MASK", Setting.SETTINGTYPE_INT, 0)
except:
    SETTING_NODE_VALID_KEYS_MASK = 0

#setOrUpdateSettingValue("NODE_VALID_KEYS_MASK", Setting.SETTINGTYPE_INT, 0x00)
