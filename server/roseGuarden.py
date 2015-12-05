__author__ = 'drobisch'
from app.server import app, db
from app.worker import backgroundWorker
from flask_script import Manager
from flask_migrate import MigrateCommand
from flask_alchemydumps import AlchemyDumpsCommand
from app.models import User, Log, Door, Setting
from app.config import SYNC_MASTER_DEFAULT_PASSWORD
import app.config as config
import datetime

manager = Manager(app, False)
manager.add_command('db', MigrateCommand)
manager.add_command('backup', AlchemyDumpsCommand)


@manager.command
def start():
    "Start RoseGuarden"
    # start backgroundworker
    backgroundWorker.run()

    # running the flask app
    app.run('0.0.0.0', threaded=True)

    # after exiting the app, cancel the backgroundowrker
    backgroundWorker.cancel()

@manager.command
def create_db():
    "Create RoseGuarden database"
    db.create_all()
    User.query.delete()

    # add syncmaster-user for synchronisation
    syncMasterUser = User('syncmaster@roseguarden.org', SYNC_MASTER_DEFAULT_PASSWORD, 'Sync','Master',1)
    syncMasterUser.syncMaster = 1

    db.session.add(syncMasterUser)

    # you can add some default user here
    defaultUser1 = User('kommando@konglomerat.org','pleasechangethepassword','Konglomerat','Kommando', 0)
    defaultUser1.accessType = 1
    defaultUser2 = User('m.drobisch@googlemail.com','1234','Marcus','Drobisch',1,'01754404298',0x00,0x03)
    defaultUser2.accessType = 1

    db.session.add(defaultUser1)
    db.session.add(defaultUser2)

    #db.session.add(User(id = 0, password = flask_bcrypt.generate_password_hash('1234'), token = base64.encodestring('m.drobisch@googlemail.com:1234'), tokenExpirationDate= datetime.datetime.utcnow(), firstName = 'Marcus', lastName = 'Drobisch', phone = '0175 4404298', email='m.drobisch@googlemail.com', card_id = '1.1.1.1' , doorLicense = 0x01, deviceLicense = 0x01))
    #db.session.add(User(id = 1, password = flask_bcrypt.generate_password_hash('1234'), token = base64.encodestring('m.mustermann@googlemail.com:1234'), tokenExpirationDate= datetime.datetime.utcnow(), firstName = 'Max', lastName = 'Mustermann', phone = '0175 4404298', email='m.mustermann@googlemail.com', card_id = '2.1.1.1'  , doorLicense = 0x00, deviceLicense = 0x00))

    Door.query.delete()
    #db.session.add(Door(id = 0, name = 'front door', address = 'http://192.168.2.137', keyMask = 0x01, local = 0x00 ))
    #db.session.add(Door(id = 0, name = 'front door', address = 'http://192.168.2.138', keyMask = 0x01, local = 0x00 ))
    #db.session.add(Door(id = 0, name = 'front door', address = 'http://192.168.2.139', keyMask = 0x01, local = 0x00 ))
    db.session.add(Door(name = 'Local door', address = 'http://localhost', keyMask = 0x03, local = 0x01 ))

    Setting.query.delete()
    db.session.add(Setting('NodeName','Test door',Setting.VALUETYPE_STRING))
    db.session.add(Setting('NodeValidKey','0x03',Setting.VALUETYPE_INT))

    Log.query.delete()
    db.session.add(Log(datetime.datetime.utcnow(), config.NODE_NAME, syncMasterUser.firstName + ' ' + syncMasterUser.lastName, syncMasterUser.email, 'Remove all data & regenerate database', 'Init systen', 'L1', 1, 'Internal'))

    db.session.commit()

if __name__ == '__main__':
    manager.run()

