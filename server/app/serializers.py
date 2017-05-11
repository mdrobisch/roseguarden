__author__ = 'drobisch'

from models import User, Action
from marshmallow import Schema, fields, post_load, post_dump
import datetime


class UserListForSupervisorsSerializer(Schema):
    class Meta:
        fields = ("id", "email", "firstName", "lastName", "phone", "role", "licenseMask", "keyMask", "lastBudgetUpdateDate",
                  "association", "accessDateStart", "accessDateEnd", "lastAccessDaysUpdateDate",
                  "accessTimeStart", "accessTimeEnd", "lastSyncDateTime", "accessType", "accessDaysMask", "accessDayCounter",
                  "budget", "cardID", "accessDayCyclicBudget")

class UserListSerializer(Schema):
    class Meta:
        fields = ("id", "email", "firstName", "lastName", "phone", "role", "licenseMask", "keyMask", "lastBudgetUpdateDate", "lastAccessDateTime",
                  "association", "registerDateTime", "lastLoginDateTime", "accessDateStart", "accessDateEnd", "lastAccessDaysUpdateDate",
                  "accessTimeStart", "accessTimeEnd", "lastSyncDateTime", "accessType", "accessDaysMask", "accessDayCounter",
                  "budget", "cardID", "accessDayCyclicBudget")

class AdminsListSerializer(Schema):
    class Meta:
        fields = ("email", "firstName", "lastName", "phone", "role", "association")

class SettingsListSerializer(Schema):
    class Meta:
        fields = ("id", "name", "value", "type")

class StatisticListSerializer(Schema):
    class Meta:
        fields = ("id", "statId", "name", "statType", "binningCount", "seriesCount", "description", "displayConfig", "seriesName1", "seriesName2", "seriesName3", "seriesName4", "seriesName5", "seriesName6", "seriesName7", "seriesName8")

class StatisticEntryListSerializer(Schema):
    class Meta:
        fields = ("id", "statId", "statId", "month", "year", "binningId", "series", "label", "value")

class UserSerializer(Schema):
    class Meta:
        fields = ("id", "email", "firstName", "lastName", "phone", "role", "licenseMask", "keyMask", "lastBudgetUpdateDate", "lastAccessDateTime",
                  "association", "registerDateTime", "lastLoginDateTime", "accessDateStart", "accessDateEnd", "lastAccessDaysUpdateDate",
                  "accessTimeStart", "accessTimeEnd", "lastSyncDateTime", "accessType", "accessDaysMask", "accessDayCounter",
                  "budget", "cardIDAssigned", "accessDayCyclicBudget")

    #@post_dump(pass_many=True)
    #def wrap_if_many(self, data, many=False):
    #    if many:
    #        return {'userList': data}
    #    return data

    #@post_load
    #def make_user(self, data):
    #    result = User("testmail","passwor","name","kasdk")
    #    return result

class UserSyncSerializer(Schema):
    class Meta:
        fields = ("id", "email", "firstName", "lastName", "phone", "role", "licenseMask", "keyMask", "lastAccessDateTime",
                  "association", "registerDateTime", "lastLoginDateTime", "lastSyncDateTime", "lastAccessDaysUpdateDate",
                  "accessDateStart", "accessDateEnd", "lastBudgetUpdateDate", "accessDayCyclicBudget",
                  "accessTimeStart", "accessTimeEnd", "accessType", "accessDaysMask", "accessDayCounter",
                  "budget", "cardID", "password", "syncMaster", "active", "cardAuthBlock", "cardAuthSector",
                  "cardID", "cardSecret", "cardAuthKeyA", "cardAuthKeyB")

    @post_load
    def make_user(self, data):
        firstName = data['firstName']
        lastName = data['lastName']
        email = data['email']
        password = data['password']

        #create base user
        user = User(email, password, firstName, lastName)

        user.updateUserFromSyncDict(data)

        #add all aditional member-vars
        user.id = data['id']
        if user.id == -1:
            user.id = None

        return user
        #return { "id": data['id'], "firstName": data['firstName'], lastName: data['lastName'], "email": email, password : password}


class SessionInfoSerializer(Schema):
    class Meta:
        fields = ("id", "role")

class RfidTagInfoSerializer(Schema):
    userInfo = fields.String()
    tagId = fields.String()
    error = fields.Bool()
    errorInfo = fields.String()
    detected = fields.Bool()

class NodeLinkSerializer(Schema):
    class Meta:
        fields = ("id", "name", "displayName", "keyMask", "address", "local", "type")

class LogSerializer(Schema):
    class Meta:
        fields = ("id", "date", "nodeName", "userName", "userMail", "authType", "authInfo", "logText", "logType", "logLevel", "rollbackPoint", "synced", "action", "actionParameter")

    @post_load
    def make_user(self, data):
        date            = datetime.datetime.strptime(data['date'][:19], '%Y-%m-%dT%H:%M:%S')
        nodeName        = data['nodeName']
        userName        = data['userName']
        userMail        = data['userMail']
        authType        = data['authType']
        authInfo        = data['authInfo']
        logText         = data['logText']
        logType         = data['logType']
        logLevel        = data['logLevel']
        rollbackPoint   = data['rollbackPoint']
        action          = data['action']
        actionParameter = data['actionParameter']

        action = Action(date,nodeName,userName,userMail,logText,logType,logLevel,authType,authInfo,action,actionParameter,rollbackPoint)

        return action

#class User_Serializer (Resource):
#    @marshal_with(parameter_marshaller)
#    def get(self, user_id):
#        entity = User.query.get(user_id)
#        return entity

