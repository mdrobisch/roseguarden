__author__ = 'drobisch'

from flask_wtf import Form

from wtforms_alchemy import model_form_factory
from wtforms import StringField
from wtforms.validators import DataRequired, Optional

from server import db
from models import User

BaseModelForm = model_form_factory(Form)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class UserCreateForm(ModelForm):
    class Meta:
        model = User

class UserPatchForm(Form):
    email = StringField('email', validators=[Optional()])
    firstName = StringField('firstName', validators=[Optional()])
    lastName = StringField('lastName', validators=[Optional()])
    phone = StringField('phone', validators=[Optional()])
    newpassword = StringField('password', validators=[Optional()])
    oldpassword = StringField('password', validators=[Optional()])

class SessionCreateForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])

class RegisterUserForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    firstName = StringField('firstName', validators=[DataRequired()])
    lastName = StringField('lastName', validators=[DataRequired()])
    phone = StringField('lastName', validators=[DataRequired()])

class LostPasswordForm(Form):
    email = StringField('email', validators=[DataRequired()])
