__author__ = 'drobisch'

from flask_restful import Resource
from models import User
from marshmallow import Serializer, fields
import datetime

class UserSerializer(Serializer):
    id = fields.Integer()
    email = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    phone = fields.String()
    role = fields.Integer()
    licenseMask = fields.Integer()
    keyMask = fields.Integer()
    lastLoginDateTime = fields.DateTime("%H:%M %d.%m.%Y")
    registerDateTime = fields.DateTime("%d.%m.%Y")
    accessDateStart = fields.DateTime("%d.%m.%Y")
    accessDateEnd = fields.DateTime("%d.%m.%Y")
    accessTimeStart = fields.DateTime("%H:%M")
    accessTimeEnd = fields.DateTime("%H:%M")
    accessType = fields.Integer()
    accessDaysMask = fields.Integer()
    accessDayCounter = fields.Integer()
    budget = fields.Float()
    #class Meta:
    #    fields = ("id", "email", "firstName", "lastName", "phone", "role", "license", "key", "accessDateTimeStart", "accessType")
    #    dateformat = "%Y "

class SessionInfoSerializer(Serializer):
    class Meta:
        fields = ("id","role")


class RequestSerializer(Serializer):
    class Meta:
        fields = ("userMail", "userName", "cardID", "requestName", "requestType", "date")

class DoorSerializer(Serializer):
    class Meta:
        fields = ("name", "keyMask", "address")

#class User_Serializer (Resource):
#    @marshal_with(parameter_marshaller)
#    def get(self, user_id):
#        entity = User.query.get(user_id)
#        return entity

