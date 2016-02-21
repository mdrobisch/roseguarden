__author__ = 'drobisch'

from flask_wtf import Form

from wtforms_alchemy import model_form_factory
from wtforms import StringField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Optional

from server import db
from models import User

BaseModelForm = model_form_factory(Form)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


#class UserCreateForm(ModelForm):
#    class Meta:
#        model = User

class UserDeleteForm(Form):
    email = StringField('email', validators=[Optional()])

class SettingPatchForm(Form):
    name = StringField('name', validators=[DataRequired()])
    value = StringField('value', validators=[DataRequired()])
    type = IntegerField('type', validators=[DataRequired()])

class UserPatchForm(Form):
    email = StringField('email', validators=[Optional()])
    firstName = StringField('firstName', validators=[Optional()])
    lastName = StringField('lastName', validators=[Optional()])
    phone = StringField('phone', validators=[Optional()])
    role = StringField('role', validators=[Optional()])
    newpassword = StringField('password', validators=[Optional()])
    oldpassword = StringField('password', validators=[Optional()])
    association = StringField('association', validators=[Optional()])

    accessType = IntegerField('accessType', validators=[Optional()])
    keyMask = IntegerField('keyMask', validators=[Optional()])
    accessDayCounter = IntegerField('accessDayCounter', validators=[Optional()])
    accessDayCyclicBudget = IntegerField('accessDayCyclicBudget', validators=[Optional()])
    accessDaysMask = IntegerField('accessDaysMask', validators=[Optional()])

    accessDateStart = StringField('accessDateStart', validators=[Optional()])
    accessDateEnd = StringField('accessDateEnd', validators=[Optional()])
    accessTimeStart = StringField('accessTimeStart', validators=[Optional()])
    accessTimeEnd = StringField('accessTimeEnd', validators=[Optional()])

class SessionCreateForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])

class RegisterUserForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    firstName = StringField('firstName', validators=[DataRequired()])
    lastName = StringField('lastName', validators=[DataRequired()])
    phone = StringField('phone', validators=[DataRequired()])
    association = StringField('association', validators=[DataRequired()])
    sendWelcomeMail = IntegerField('sendWelcomeMail', validators=[Optional()])

class LostPasswordForm(Form):
    email = StringField('email', validators=[DataRequired()])


class DoorRegistrationForm(Form):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])

class RFIDTagAssignForm(Form):
    email = StringField('email', validators=[DataRequired()])
    rfidTagId = StringField('rfidTagId', validators=[DataRequired()])

class RFIDTagWithdrawForm(Form):
    email = StringField('email', validators=[DataRequired()])
    rfidTagId = StringField('rfidTagId', validators=[DataRequired()])
