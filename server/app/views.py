__author__ = 'drobisch'
from email import send_email
from flask import g, render_template, make_response, jsonify, request
from flask_restful import Resource, fields, marshal_with
from server import api, db, flask_bcrypt, auth, mail
from models import User, Action, Door, RfidTagInfo
from serializers import LogSerializer, UserSyncSerializer, UserSerializer, SessionInfoSerializer, DoorSerializer, RfidTagInfoSerializer
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
        return UserSerializer().dump(user).data

    @auth.login_required
    def delete(self, id):
        user = User.query.filter_by(id=id).first()
        if user != None:
            print 'delete user ' + user.firstName + ' ' + user.lastName + ' (' + user.email + ') from database'

            logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
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
        log_text = ''
        if form.newpassword.data != None and form.newpassword.data != '':
            oldpwd = base64.decodestring(form.oldpassword.data)
            if not flask_bcrypt.check_password_hash(user.password, oldpwd):
                print 'incoorect old password'
                return make_response(jsonify({'error': 'Not authorized'}), 403)
            print 'correct old password'
            if log_text != '':
                log_text += '; '
            log_text += 'Changed password'
            user.password = flask_bcrypt.generate_password_hash(base64.decodestring(form.newpassword.data))
            db.session.commit()
        if form.lastName.data != None and form.lastName.data != '':
            if user.lastName != form.lastName.data:
                if log_text != '':
                    log_text += '; '
                log_text += 'Change last name from ' + user.lastName + ' to ' + form.lastName.data
            user.lastName = form.lastName.data
        if form.firstName.data != None and form.firstName.data != '':
            if user.firstName != form.firstName.data:
                if log_text != '':
                    log_text += '; '
                log_text += 'Change first name from ' + user.firstName + ' to ' + form.firstName.data
            user.firstName = form.firstName.data
        if form.phone.data != None and form.phone.data != '':
            if user.phone != form.phone.data:
                if log_text != '':
                    log_text += '; '
                log_text +=  'Change phone number from ' + user.phone + ' to ' + form.phone.data
            user.phone = form.phone.data
        if form.role.data != None and form.role.data != '':
            if user.role != form.role.data:
                if log_text != '':
                    log_text += '; '
                log_text += 'Change role from ' + str(user.role) + ' to ' + str(form.role.data)
            user.role = form.role.data
        if form.association.data != None and form.association.data != '':
            if user.association != form.association.data:
                if log_text != '':
                    log_text += '; '
                log_text += 'Change association to ' + str(form.association.data)
            user.association = form.association.data
        if form.accessDaysMask.data != None and form.accessDaysMask.data != '':
            if user.accessDaysMask != form.accessDaysMask.data:
                if log_text != '':
                    log_text += '; '
                log_text += 'Change accessDaysMask from ' + str(user.accessDaysMask) + ' to ' + str(form.accessDaysMask.data)
            user.accessDaysMask = form.accessDaysMask.data
        if form.accessDayCounter.data != None and form.accessDayCounter.data != '':
            if user.accessDayCounter != form.accessDayCounter.data:
                if log_text != '':
                    log_text += '; '
                log_text += 'Change accessDayCounter from ' + str(user.accessDayCounter) + ' to ' + str(form.accessDayCounter.data)
                user.lastAccessDaysUpdateDate = datetime.datetime.today()
            user.accessDayCounter = form.accessDayCounter.data
        if form.accessDayCyclicBudget.data != None and form.accessDayCyclicBudget.data != '':
            if user.accessDayCyclicBudget != form.accessDayCyclicBudget.data:
                if log_text != '':
                    log_text += '; '
                log_text += 'Change accessDayCyclicBudget from ' + str(user.accessDayCyclicBudget) + ' to ' + str(form.accessDayCyclicBudget.data)
                user.lastAccessDaysUpdateDate = datetime.datetime.today()
            user.accessDayCyclicBudget = form.accessDayCyclicBudget.data
        if form.accessType.data != None and form.accessType.data != '':
            if user.accessType != form.accessType.data:
                if log_text != '':
                    log_text += '; '
                log_text += 'Change accessType from ' + str(user.accessType) + ' to ' + str(form.accessType.data)
                user.lastAccessDaysUpdateDate = datetime.datetime.today()
            user.accessType = form.accessType.data
        if form.keyMask.data != None and form.keyMask.data != '':
            if user.keyMask != form.keyMask.data:
                if log_text != '':
                    log_text += '; '
                log_text += 'Change keyMask from ' + str(user.keyMask) + ' to ' + str(form.keyMask.data)
            user.keyMask = form.keyMask.data
        if form.accessDateStart.data != None and form.accessDateStart.data != '':
            if user.accessDateStart != datetime.datetime.strptime(form.accessDateStart.data, '%Y-%m-%dT%H:%M:%S.%fZ'):
                if log_text != '':
                    log_text += '; '
                log_text += 'Change accessDateStart from ' + str(user.accessDateStart) + ' to ' + str(form.accessDateStart.data)
            user.accessDateStart = datetime.datetime.strptime(form.accessDateStart.data, '%Y-%m-%dT%H:%M:%S.%fZ')
        if form.accessDateEnd.data != None and form.accessDateEnd.data != '':
            if user.accessDateEnd != datetime.datetime.strptime(form.accessDateEnd.data, '%Y-%m-%dT%H:%M:%S.%fZ'):
                if log_text != '':
                    log_text += '; '
                log_text += 'Change accessDateEnd from ' + str(user.accessDateEnd ) + ' to ' + str(form.accessDateEnd.data)
            user.accessDateEnd = datetime.datetime.strptime(form.accessDateEnd.data, '%Y-%m-%dT%H:%M:%S.%fZ')
        if form.accessTimeStart.data != None and form.accessTimeStart.data != '':
            if user.accessTimeStart != datetime.datetime.strptime(form.accessTimeStart.data, '%Y-%m-%dT%H:%M:%S.%fZ'):
                if log_text != '':
                    log_text += '; '
                log_text += 'Change accessTimeStart from ' + str(user.accessTimeStart) + ' to ' + str(form.accessTimeStart.data)
            user.accessTimeStart = datetime.datetime.strptime(form.accessTimeStart.data, '%Y-%m-%dT%H:%M:%S.%fZ')
        if form.accessTimeEnd.data != None and form.accessTimeEnd.data != '':
            if user.accessTimeEnd != datetime.datetime.strptime(form.accessTimeEnd.data, '%Y-%m-%dT%H:%M:%S.%fZ'):
                if log_text != '':
                    log_text += '; '
                log_text += 'Change accessTimeEnd from ' + str(user.accessTimeEnd) + ' to ' + str(form.accessTimeEnd.data)
            user.accessTimeEnd = datetime.datetime.strptime(form.accessTimeEnd.data, '%Y-%m-%dT%H:%M:%S.%fZ')

        log_text = 'Update of ' + user.firstName + ' ' + user.lastName + ' (' + user.email + ')' + ' with the following changes: ' + log_text
        logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
                       g.user.email, log_text, 'User updated',
                       'L1', 0, 'Web based')
        db.session.add(logentry)
        db.session.commit()

        return '', 201


class UserListView(Resource):
    @auth.login_required
    def get(self):
        users = User.query.filter_by(syncMaster=0).all()
        return UserSerializer().dump(users, many=True).data

    def post(self):
        counter = 0
        if request.json['userList'] != None:
            #print str(request.json['userList'])
            print datetime.datetime.now()
            try:
                dbUserDeletetionList = User.query.filter(User.syncMaster == 0).all()
                for userItem in request.json['userList']:
                    newuser_detected = True
                    for dbUser in dbUserDeletetionList:
                        if userItem['id'] == dbUser.id:
                            # print the
                            print dbUser.email + " found in list and will get updated"
                            # remove user from deletion List
                            dbUser.updateUserFromSyncDict(userItem)
                            dbUser.lastSyncDateTime = datetime.datetime.now()
                            dbUserDeletetionList.remove(dbUser)
                            newuser_detected = False
                            break
                        else:
                            if userItem['email'] == dbUser.email:
                                newuser_detected = False
                    if newuser_detected == True:
                        print userItem['email'] + " as new user detected"
                        newUser = UserSyncSerializer().load(userItem).data
                        db.session.add(newUser)

                db.session.commit()

                #delete remaining users not found in the request-user-list
                for dbUser in dbUserDeletetionList:
                    print dbUser.email + " not found in the sync-list and will get deleted"
                    db.session.delete(dbUser)

                    #requestUser = UserSyncSerializer().load(userItem).data
                    #db.session.add(requestUser)
                    #databaseUser = User.query.filter_by(id=1).first()

                db.session.commit()

            except:
                print 'failure detected'
                db.session.rollback()
                raise
            print datetime.datetime.now()
        return '', 201

class RegisterUserView(Resource):
    def post(self):
        form = RegisterUserForm()
        print 'enter registerview'
        if not form.validate_on_submit():
            return form.errors, 422
        pwd = base64.decodestring(form.password.data)
        user = User(email=form.email.data, password=pwd, firstName=form.firstName.data, lastName=form.lastName.data,
                    phone=form.phone.data, association=form.association.data)
        logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, user.firstName + ' ' + user.lastName, user.email,
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
            logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, user.firstName + ' ' + user.lastName,
                           user.email, 'User login', 'User login', 'L2', 0, 'Web based')
            try:
                db.session.add(logentry)
                db.session.commit()
            except:
                raise
                return '', 201
            return SessionInfoSerializer().dump(user).data, 201
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

class DoorSyncView(Resource):
    #@auth.login_required
    def post(self, id):
        print 'Sync. request '
        for userItem in globals.request.json:
            print userItem
        return '', 201


class OpeningRequestView(Resource):
    @auth.login_required
    def post(self):
        print 'Opening request received'
        checkAccessResult = g.user.checkUserAccessPrivleges()
        if (checkAccessResult == "Access granted."):

            logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
                           g.user.email, 'Opening request', 'Opening request', 'L2', 0, 'Web based', Action.ACTION_OPENING_REQUEST)
            try:
                db.session.add(logentry)
                db.session.commit()
            except:
                return '', 401
            backgroundWorker.requestOpening = True
            print "Check user privileges for opening request: " + checkAccessResult
            return 'Access granted', 201
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
            logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
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

        pwd = base64.b64decode(form.password.data)
        auth_token = 'Basic ' + base64.b64encode("syncmaster@roseguarden.org:" + pwd)
        headers = {'Authorization' : auth_token}

        try:
            response = requests.get('http://' + form.address.data + ':5000' + '/request/doorinfo', timeout=4, headers = headers)
        except:
            print "requested door unreachable"
            return 'requested door unreachable', 400

        response_data = json.loads(response.content)
        newDoor = Door(name=response_data["name"], displayName= form.name.data, keyMask=response_data["keyMask"], address='http://' + form.address.data,
                       local=0, password = pwd)
        logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
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
        return DoorSerializer().dump(newDoor).data


class DoorInfoView(Resource):
    @auth.login_required
    def get(self):
        print 'Door info request'
        localdoor = Door.query.filter_by(local=1).first()
        return DoorSerializer().dump(localdoor).data


class DoorListView(Resource):
    @auth.login_required
    def get(self):
        posts = Door.query.filter_by(local=0).all()
        return DoorSerializer().dump(posts, many=True).data


class LogAdminView(Resource):
    @auth.login_required
    def get(self):
        if (g.user.role & 1) == 0 and (g.user.syncMaster == 0):
            return make_response(jsonify({'error': 'Not authorized'}), 403)
        logs = Action.query.order_by(Action.date.desc()).all()
        return LogSerializer().dump(logs, many=True).data

    @auth.login_required
    def delete(self):
        if (g.user.syncMaster == 0):
            return make_response(jsonify({'error': 'Not authorized'}), 403)

        print 'action-log deletetion requested'
        Action.query.delete()
        logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
                       '', 'Removed all actions after syncing', 'Remove actions after sync',
                       'L1', 0, 'Web based')
        db.session.add(logentry)
        db.session.commit()
        return '', 201


class LogUserView(Resource):
    @auth.login_required
    def get(self):
        logs = Action.query.filter_by(userMail=g.user.email).order_by(Action.date.desc()).all()
        return LogSerializer().dump(logs, many=True).data


class RfidTagInfoView(Resource):
    @auth.login_required
    def get(self):
        print backgroundWorker.tagInfo.userInfo + ' ' + backgroundWorker.tagInfo.tagId
        return RfidTagInfoSerializer().dump(backgroundWorker.tagInfo).data


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
                logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
                               g.user.email, 'Assign RFID-tag ' + form.rfidTagId.data + ' to ' + user.firstName + ' ' + user.lastName, 'Card administration',
                               'L1', 0, 'Card based')
                db.session.add(logentry)
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
                logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
                               g.user.email, 'Withdraw cardID-tag ' + form.rfidTagId.data + ' from ' + user.firstName + ' ' + user.lastName, 'Card administration',
                               'L1', 0, 'Web based')
                db.session.add(logentry)
                db.session.commit()

                return '', 201
        else:
            return make_response(jsonify({'error': 'bad request data'}), 400)


api.add_resource(SessionView, '/sessions')

api.add_resource(UserView, '/user/<int:id>')
api.add_resource(UserListView, '/users')

api.add_resource(LogUserView, '/actions/user')
api.add_resource(LogAdminView, '/actions/admin')

api.add_resource(DoorView, '/door/<int:id>')
api.add_resource(DoorSyncView, '/door/<int:id>/sync')
api.add_resource(DoorRegistrationView, '/door')
api.add_resource(DoorListView, '/doors')

api.add_resource(OpeningRequestView, '/request/opening')
api.add_resource(LostPasswordView, '/request/password')
api.add_resource(DoorInfoView, '/request/doorinfo')

api.add_resource(RfidTagInfoView, '/tag/info')
api.add_resource(RfidTagAssignView, '/tag/assign')
api.add_resource(RfidTagWitdrawView, '/tag/withdraw')
api.add_resource(RegisterUserView, '/register')
