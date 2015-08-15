__author__ = 'drobisch'

from flask_restful import Resource
from models import User
from marshmallow import Serializer, fields

class UserSerializer(Serializer):
    class Meta:
        fields = ("id", "email", "firstName", "lastName", "phone", "role", "license", "key")

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

