__author__ = 'drobisch'

from flask_restful import Resource
from models import User
from marshmallow import Schema, fields, post_load, post_dump
import datetime

class UserSerializer(Schema):
    class Meta:
        fields = ("id", "email", "firstName", "lastName", "phone", "role", "licenseMask", "keyMask",
                  "association", "registerDateTime", "lastLoginDateTime", "accessDateStart", "accessDateEnd",
                  "accessTimeStart", "accessTimeEnd", "accessType", "accessDaysMask", "accessDayCounter",
                  "budget", "cardID")

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
        fields = ("id", "email", "firstName", "lastName", "phone", "role", "licenseMask", "keyMask",
                  "association", "registerDateTime", "lastLoginDateTime", "accessDateStart", "accessDateEnd",
                  "accessTimeStart", "accessTimeEnd", "accessType", "accessDaysMask", "accessDayCounter",
                  "budget", "cardID", "password")
    @post_load
    def make_user(self, data):
        firstName = data['firstName']
        lastName = data['lastName']
        email = data['email']
        password = data['password']
        result = User(email, password, firstName, lastName)
        return result


class SessionInfoSerializer(Schema):
    class Meta:
        fields = ("id", "role")

class RfidTagInfoSerializer(Schema):
    userInfo = fields.String()
    tagId = fields.String()

class DoorSerializer(Schema):
    class Meta:
        fields = ("id", "name", "keyMask", "address", "local")

class LogSerializer(Schema):
    class Meta:
        fields = ("id", "date", "nodeName", "userName", "userMail", "authType", "authInfo", "logText", "logType", "logLevel")


#class User_Serializer (Resource):
#    @marshal_with(parameter_marshaller)
#    def get(self, user_id):
#        entity = User.query.get(user_id)
#        return entity

