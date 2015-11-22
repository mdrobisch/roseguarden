__author__ = 'drobisch'

from flask_restful import Resource
from models import User
from marshmallow import Serializer, fields
import datetime

class UserSerializer(Serializer):
    class Meta:
        fields = ("id", "email", "firstName", "lastName", "phone", "role", "licenseMask", "keyMask",
                  "association", "registerDateTime", "lastLoginDateTime", "accessDateStart", "accessDateEnd",
                  "accessTimeStart", "accessTimeEnd", "accessType", "accessDaysMask", "accessDayCounter",
                  "budget", "cardID")

class SessionInfoSerializer(Serializer):
    class Meta:
        fields = ("id", "role")

class RfidTagInfoSerializer(Serializer):
    userInfo = fields.String()
    tagId = fields.String()

class DoorSerializer(Serializer):
    class Meta:
        fields = ("id", "name", "keyMask", "address", "local")

class LogSerializer(Serializer):
    class Meta:
        fields = ("id", "date", "nodeName", "userName", "userMail", "authType", "authInfo", "logText", "logType", "logLevel")


#class User_Serializer (Resource):
#    @marshal_with(parameter_marshaller)
#    def get(self, user_id):
#        entity = User.query.get(user_id)
#        return entity

