__author__ = 'drobisch'
from email import send_email
from flask import g, render_template, make_response, jsonify
from flask_restful import Resource, fields, marshal_with
from server import api, db, flask_bcrypt, auth, mail
from models import User, Log, Door, RfidTagInfo
from serializers import LogSerializer, UserSerializer, SessionInfoSerializer, DoorSerializer, RfidTagInfoSerializer
from forms import UserPatchForm, DoorRegistrationForm, SessionCreateForm, LostPasswordForm, RegisterUserForm, \
    UserDeleteForm, RFIDTagAssignForm, RFIDTagWithdrawForm
from worker import backgroundWorker
from sqlalchemy.exc import IntegrityError
import config
import json
import random
import requests
import base64
import controller
import datetime


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
    def delete(self, id):
        user = User.query.filter_by(id=id).first()
        if user != None:
            print 'delete user ' + user.firstName + ' ' + user.lastName + ' (' + user.email + ') from database'

            logentry = Log(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
                           g.user.email, 'User ' + user.firstName + ' on ' + user.lastName + ' removed', 'User removed',
                           'L1', 1, 'Web based')
            db.session.add(logentry)
            db.session.commit()

            User.query.filter(User.id == id).delete()
            db.session.commit()
        return '', 201

    @auth.login_required
    def post(self, id):
        if id != g.user.id:
            if (g.user.role & 1) == 0:
                return make_response(jsonify({'error': 'Not authorized'}), 403)
        form = UserPatchForm()
        if not form.validate_on_submit():
            print form.errors
            return form.errors, 422
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
        if form.role.data != None and form.role.data != '':
            print 'Change role to ' + str(form.role.data)
            user.role = form.role.data
        if form.association.data != None and form.association.data != '':
            print 'Change association to ' + str(form.association.data)
            user.association = form.association.data
        if form.accessDaysMask.data != None and form.accessDaysMask.data != '':
            print 'Change accessDaysMask to ' + str(form.accessDaysMask.data)
            user.accessDaysMask = form.accessDaysMask.data
        if form.accessDayCounter.data != None and form.accessDayCounter.data != '':
            print 'Change accessDayCounter to ' + str(form.accessDayCounter.data)
            user.accessDayCounter = form.accessDayCounter.data
        if form.accessType.data != None and form.accessType.data != '':
            print 'Change accessType to ' + str(form.accessType.data)
            user.accessType = form.accessType.data
        if form.keyMask.data != None and form.keyMask.data != '':
            print 'Change keyMask to ' + str(form.keyMask.data)
            user.keyMask = form.keyMask.data
        if form.accessDateStart.data != None and form.accessDateStart.data != '':
            print 'Change accessDateStart to ' + str(form.accessDateStart.data)
            user.accessDateStart = datetime.datetime.strptime(form.accessDateStart.data, '%Y-%m-%dT%H:%M:%S.%fZ')
        if form.accessDateEnd.data != None and form.accessDateEnd.data != '':
            print 'Change accessDateEnd to ' + str(form.accessDateEnd.data)
            user.accessDateEnd = datetime.datetime.strptime(form.accessDateEnd.data, '%Y-%m-%dT%H:%M:%S.%fZ')
        if form.accessTimeStart.data != None and form.accessTimeStart.data != '':
            print 'Change accessTimeStart to ' + str(form.accessTimeStart.data)
            user.accessTimeStart = datetime.datetime.strptime(form.accessTimeStart.data, '%Y-%m-%dT%H:%M:%S.%fZ')
        if form.accessTimeEnd.data != None and form.accessTimeEnd.data != '':
            print 'Change accessTimeEnd to ' + str(form.accessTimeEnd.data)
            user.accessTimeEnd = datetime.datetime.strptime(form.accessTimeEnd.data, '%Y-%m-%dT%H:%M:%S.%fZ')

        db.session.commit()

        return '', 201


class UserListView(Resource):
    @auth.login_required
    def get(self):
        users = User.query.filter_by(syncMaster=0).all()

        return UserSerializer(users, many=True).data


class RegisterUserView(Resource):
    def post(self):
        form = RegisterUserForm()
        print 'enter registerview'
        if not form.validate_on_submit():
            return form.errors, 422
        pwd = base64.decodestring(form.password.data)
        user = User(email=form.email.data, password=pwd, firstName=form.firstName.data, lastName=form.lastName.data,
                    phone=form.phone.data, association=form.association.data)
        logentry = Log(datetime.datetime.utcnow(), config.NODE_NAME, user.firstName + ' ' + user.lastName, user.email,
                       'User registered ' + user.firstName + ' ' + user.lastName + ' ' + user.email, 'User registered',
                       'L1', 1, 'Web based')

        try:
            db.session.add(logentry)
            db.session.commit()
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            return make_response(jsonify({'error': 'eMail already registered'}), 400)

        # if activted send email
        if form.sendWelcomeMail.data != None:
            print 'sendWelcomeMail is ' + str(form.sendWelcomeMail.data)
            if form.sendWelcomeMail.data == 1:
                print 'try to send welcome mail'
                try:
                    send_email("Welcome to %s. You successfully registered" % 'RoseGuarden',
                               config.MAIL_USERNAME,
                               [user.email],
                               render_template("welcome_mail.txt",
                                               user=user),
                               render_template("welcome_mail.html",
                                               user=user))
                except:
                    print 'unable to send mail'
                    return '', 201
        return '', 201


class SessionView(Resource):
    def post(self):
        form = SessionCreateForm()
        if not form.validate_on_submit():
            return form.errors, 422

        user = User.query.filter_by(email=form.email.data).first()
        if user and flask_bcrypt.check_password_hash(user.password, form.password.data):
            logentry = Log(datetime.datetime.utcnow(), config.NODE_NAME, user.firstName + ' ' + user.lastName,
                           user.email, 'User login', 'User login', 'L2', 1, 'Web based')
            try:
                db.session.add(logentry)
                db.session.commit()
            except:
                return '', 201
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
                   config.MAIL_USERNAME,
                   [user.email],
                   render_template("lostpassword_mail.txt",
                                   user=user, password=new_password),
                   render_template("lostpassword_mail.html",
                                   user=user, password=new_password))
        return '', 201


class OpeningRequestView(Resource):
    @auth.login_required
    def post(self):
        print 'Opening request received'
        checkAccessResult = g.user.checkUserAccessPrivleges()
        if (checkAccessResult == "access granted"):

            logentry = Log(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
                           g.user.email, 'Opening request', 'Opening request', 'L2', 1, 'Web based')
            try:
                db.session.add(logentry)
                db.session.commit()
            except:
                return '', 401

            backgroundWorker.requestOpening = True
            print "Check user privileges for opening request: " + checkAccessResult
            return '', 201
        else:
            print "Check user privileges for opening request: " + checkAccessResult
            return checkAccessResult, 201
        return '', 201


class DoorView(Resource):
    @auth.login_required
    def delete(self, id):
        print "requested door remove " + str(id)
        door = Door.query.filter_by(id=id).first()
        if door != None:
            print 'delete door ' + door.name + ' ' + door.address + ' (id=' + str(door.id) + ') from database'
            logentry = Log(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
                           g.user.email, 'Door (' + door.name + ' on ' + door.address + ') removed', 'Door removed',
                           'L1', 1, 'Web based')
            try:
                db.session.add(logentry)
                db.session.commit()
                Door.query.filter(Door.id == id).delete()
                db.session.commit()
            except:
                return '', 401
        return '', 201


class DoorRegistrationView(Resource):
    @auth.login_required
    def post(self):
        form = DoorRegistrationForm()
        print 'Door registration request received'
        if not form.validate_on_submit():
            return form.errors, 422

        if (g.user.role & 1) == 0:
            return make_response(jsonify({'error': 'Not authorized'}), 403)

        print 'Request door info from ' + 'http://' + form.address.data + ':5000' + '/request/doorinfo'
        try:
            response = requests.get('http://' + form.address.data + ':5000' + '/request/doorinfo', timeout=2)
        except:
            print "requested door unreachable"
            return 'requested door unreachable', 400

        print "create new door"
        response_data = json.loads(response.content)
        newDoor = Door(name=form.name.data, keyMask=response_data["keyMask"], address='http://' + form.address.data,
                       local=0)
        logentry = Log(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
                       g.user.email, 'Door ' + newDoor.name + ' on ' + newDoor.address + ' checked and registered',
                       'Door registered', 'L1', 1, 'Web based')
        try:
            db.session.add(logentry)
            db.session.commit()
            db.session.add(newDoor)
            db.session.commit()
            print "Added door to database"
        except IntegrityError:
            print "Problems to add door to database"
            return make_response(jsonify({'error': 'eMail already registered'}), 400)

        print "return new door data for request"
        return DoorSerializer(newDoor).data


class DoorInfoView(Resource):
    def get(self):
        print 'Door info request'
        localdoor = Door.query.filter_by(local=1).first()
        return DoorSerializer(localdoor).data


class DoorListView(Resource):
    @auth.login_required
    def get(self):
        posts = Door.query.filter_by(local=0).all()
        return DoorSerializer(posts, many=True).data


class LogAdminView(Resource):
    @auth.login_required
    def get(self):
        if (g.user.role & 1) == 0:
            return make_response(jsonify({'error': 'Not authorized'}), 403)
        logs = Log.query.all()
        return LogSerializer(logs, many=True).data


class LogUserView(Resource):
    @auth.login_required
    def get(self):
        logs = Log.query.filter_by(userMail=g.user.email).all()
        return LogSerializer(logs, many=True).data


class RfidTagInfoView(Resource):
    @auth.login_required
    def get(self):
        print backgroundWorker.tagInfo.userInfo + ' ' + backgroundWorker.tagInfo.tagId
        return RfidTagInfoSerializer(backgroundWorker.tagInfo).data


class RfidTagAssignView(Resource):
    @auth.login_required
    def post(self):
        print 'RFID assign request received'
        # check request paremeters (form)
        form = RFIDTagAssignForm()
        if not form.validate_on_submit():
            return form.errors, 422
        # check admin rights
        if (g.user.role & 1) == 0:
            return make_response(jsonify({'error': 'Not authorized'}), 403)

        user = User.query.filter_by(email=form.email.data).first()

        if (user == None):
            return make_response(jsonify({'error': 'user not found'}), 400)

        if form.rfidTagId.data != None and form.rfidTagId.data != '':

            secretString = ''
            for i in range(0,16):
                if i != 0:
                    secretString = secretString + '-'
                num = random.randrange(0, 256)
                secretString = secretString + format(num, '02X')

            user.cardID = form.rfidTagId.data
            user.cardSecret = secretString
            user.cardAuthBlock = 1
            user.cardAuthSector = 4
            user.cardAuthKeyA = config.RFID_GLOBAL_PASSWORD
            user.cardAuthKeyB = "FF-FF-FF-FF-FF-FF"

            print "User-secret: >" + user.cardSecret + "<"
            print "User-keyA: >" + user.cardAuthKeyA + "<"
            print "User-keyB: >" + user.cardAuthKeyB + "<"

            if (backgroundWorker.assignRFIDTag(user) == False):
                print 'Error while assigning cardID ' + form.rfidTagId.data + ' to ' + user.firstName + ' ' + user.lastName
                db.session.rollback()
                return make_response(jsonify({'error': 'user not found'}), 400)
            else:
                db.session.commit()

        print 'Assigned cardID ' + form.rfidTagId.data + ' to ' + user.firstName + ' ' + user.lastName
        return '', 201


class RfidTagWitdrawView(Resource):
    @auth.login_required
    def post(self):
        print 'RFID withdraw request received'
        # check request paremeters (form)
        form = RFIDTagAssignForm()
        if not form.validate_on_submit():
            return form.errors, 422
        # check admin rights
        if (g.user.role & 1) == 0:
            return make_response(jsonify({'error': 'Not authorized'}), 403)

        user = User.query.filter_by(email=form.email.data).first()

        if (user == None):
            return make_response(jsonify({'error': 'user not found'}), 400)

        if form.rfidTagId.data is not None and form.rfidTagId.data != '':
            if not backgroundWorker.withdrawRFIDTag(user):
                print 'Error while withdraw cardID ' + user.cardID + ' from ' + user.firstName + ' ' + user.lastName
                db.session.rollback()
                return make_response(jsonify({'error': 'user not found'}), 400)
            else:
                user.cardID = ''
                user.cardSecret = ''
                user.cardAuthKeyA = ''
                user.cardAuthKeyB = ''
                db.session.commit()
                print 'Withdraw cardID ' + form.rfidTagId.data + ' from ' + user.firstName + ' ' + user.lastName
                return '', 201
        else:
            return make_response(jsonify({'error': 'bad request data'}), 400)


api.add_resource(SessionView, '/sessions')
api.add_resource(UserView, '/user/<int:id>')
api.add_resource(UserListView, '/users')
api.add_resource(LogUserView, '/log/user')
api.add_resource(LogAdminView, '/log/admin')
api.add_resource(DoorView, '/door/<int:id>')
api.add_resource(DoorRegistrationView, '/door')
api.add_resource(DoorListView, '/doors')
api.add_resource(OpeningRequestView, '/request/opening')
api.add_resource(LostPasswordView, '/request/password')
api.add_resource(DoorInfoView, '/request/doorinfo')
api.add_resource(RfidTagInfoView, '/tag/info')
api.add_resource(RfidTagAssignView, '/tag/assign')
api.add_resource(RfidTagWitdrawView, '/tag/withdraw')
api.add_resource(RegisterUserView, '/register')
