__author__ = 'drobisch'
from config import MAIL_USERNAME
from email import send_email
from flask import g, render_template, make_response, jsonify
from flask_restful import Resource, fields, marshal_with
from server import api, db, flask_bcrypt, auth, mail
from models import User, Door, Request
from serializers import UserSerializer, SessionInfoSerializer, DoorSerializer, RequestSerializer
from forms import UserCreateForm,UserPatchForm, SessionCreateForm, LostPasswordForm, RegisterUserForm
from worker import backgroundWorker
from sqlalchemy.exc import IntegrityError
import base64
import controller


@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    g.user = user
    return flask_bcrypt.check_password_hash(user.password, password)


class UserView(Resource):
    @auth.login_required
    def get(self, id):
        if id != g.user.id:
            if (g.user.role & 1) == 0:
                return make_response(jsonify({'error': 'Not authorized'}), 403)
        user = User.query.filter_by(id=id).first()
        return UserSerializer(user).data

    @auth.login_required
    def post(self, id):
        if id != g.user.id:
            if (g.user.role & 1) == 0:
                return make_response(jsonify({'error': 'Not authorized'}), 403)
        form = UserPatchForm()
        if not form.validate_on_submit():
            return form.errors,422
        user = User.query.filter_by(id=id).first()
        if form.newpassword.data != None and form.newpassword.data != '':
            print 'Change password' + base64.decodestring(form.newpassword.data)
            oldpwd = base64.decodestring(form.oldpassword.data)
            if not flask_bcrypt.check_password_hash(user.password, oldpwd):
                print 'incoorect old password'
                return make_response(jsonify({'error': 'Not authorized'}), 403)
            print 'correct old password'
            user.password = flask_bcrypt.generate_password_hash(base64.decodestring(form.newpassword.data))
            db.session.commit()
        if form.lastName.data != None and form.lastName.data != '':
            print 'Change last name'
            user.lastName = form.lastName.data
        if form.firstName.data != None and form.firstName.data != '':
            print 'Change first name'
            user.firstName = form.firstName.data
        if form.phone.data != None and form.phone.data != '':
            print 'Change phone number'
            user.phone = form.phone.data
        db.session.commit()
        return '', 201


class UserViewList(Resource):
    @auth.login_required
    def get(self):
        users = User.query.all()
        return UserSerializer(users, many=True).data

class UserLogView(Resource):
    @auth.login_required
    def get(self,id):
        requests = Request.query.filter_by(id=id).all()
        if id != g.user.id:
            if (g.user.role & 1) == 0:
                return '',401
        return RequestSerializer(requests, many=True).data

class RegisterUserView(Resource):
    def post(self):
        form = RegisterUserForm()
        if not form.validate_on_submit():
            return form.errors,422
        pwd = base64.decodestring(form.password.data)
        user = User(email = form.email.data, password = pwd,firstName = form.firstName.data, lastName = form.lastName.data, phone= form.phone.data)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            return make_response(jsonify({'error': 'eMail already registered'}), 400)
        send_email("Welcome to %s. You successfully registered" % 'RoseGuarden',
           MAIL_USERNAME,
           [user.email],
           render_template("welcome_mail.txt",
                           user=user),
           render_template("welcome_mail.html",
                           user=user))
        return '', 201

class SessionView(Resource):
    def post(self):
        form = SessionCreateForm()
        if not form.validate_on_submit():
            return form.errors, 422

        user = User.query.filter_by(email=form.email.data).first()
        if user and flask_bcrypt.check_password_hash(user.password, form.password.data):
            return SessionInfoSerializer(user).data, 201
        return '', 401

class LostPasswordView(Resource):
    def post(self):
        form = LostPasswordForm()
        if not form.validate_on_submit():
            return form.errors, 422
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return '', 401
        new_password = controller.id_generator(12)
        user.password = flask_bcrypt.generate_password_hash(new_password)
        db.session.commit()
        send_email("%s: A new password has been generated" % 'RoseGuarden',
           MAIL_USERNAME,
           [user.email],
           render_template("lostpassword_mail.txt",
                           user=user,password=new_password),
           render_template("lostpassword_mail.html",
                           user=user,password=new_password))
        return '', 201


class OpeningRequestView(Resource):
    @auth.login_required
    def post(self):
        backgroundWorker.requestOpening = True
        print 'Opening request received'
        return '', 201


class DoorListView(Resource):
    @auth.login_required
    def get(self):
        posts = Door.query.all()
        return DoorSerializer(posts, many=True).data



api.add_resource(SessionView, '/sessions')
api.add_resource(UserView, '/user/<int:id>')
api.add_resource(UserLogView, '/log/user/<int:id>')
api.add_resource(DoorListView, '/doors')
api.add_resource(OpeningRequestView, '/request/opening')
api.add_resource(LostPasswordView, '/request/password')
api.add_resource(RegisterUserView, '/register')