__author__ = 'drobisch'
from app.server import app, db
from app.worker import backgroundWorker
from app.statistics import StatisticsManager
from flask_script import Manager, Option
from flask_migrate import MigrateCommand
from flask_alchemydumps import AlchemyDumpsCommand
from app.models import User, Action, Door, Setting, Statistic, StatisticEntry
from app.config import SYNC_MASTER_DEFAULT_PASSWORD
import app.config as config
import datetime
import random


manager = Manager(app, False)
manager.add_command('db', MigrateCommand)
manager.add_command('backup', AlchemyDumpsCommand)

@manager.command
def start():
    "Start RoseGuarden"
    # start backgroundworker
    backgroundWorker.run()

    StatisticsManager.raiseEvent(StatisticsManager.STATISTICS_STATID_ACCESSES)
    # running the flask app
    app.run('0.0.0.0', threaded=True)

    # after exiting the app, cancel the backgroundowrker
    backgroundWorker.cancel()

@manager.command
def open_the_door():
    "Force the local door openend"
    backgroundWorker.run()
    backgroundWorker.open_the_door()

@manager.command
def seed_statistic():
    "Create RoseGuarden database filled with testdata for the statistics"
    Statistic.query.delete()
    StatisticEntry.query.delete()

    userCountStat = Statistic("User total", StatisticsManager.STATISTICS_STATID_USERCOUNT, Statistic.STATTYPE_LINE_SERIES, 0, 3, "Users", "Admins", "Supervisors")
    accessesStat = Statistic("Accesses total", StatisticsManager.STATISTICS_STATID_ACCESSES, Statistic.STATTYPE_LINE_SERIES, 0, 2, "Card auth.", "Web auth.")
    weekdayStat = Statistic("Accesses per weekday", StatisticsManager.STATISTICS_STATID_WEEKDAYS, Statistic.STATTYPE_RADAR_SERIES, 7, 1, "Weekdays")
    doorStat = Statistic("Accesses per door", StatisticsManager.STATISTICS_STATID_DOORS, Statistic.STATTYPE_DOUGHNUT_CLASSES, 2, 0)
    loginsCountStat = Statistic("Logins", StatisticsManager.STATISTICS_STATID_LOGINS, Statistic.STATTYPE_LINE_SERIES, 0, 2, "Logins", "Failed attempts")

    db.session.add(userCountStat)
    db.session.add(accessesStat)
    db.session.add(doorStat)
    db.session.add(loginsCountStat)
    db.session.add(weekdayStat)

    # add entry for usercount
    for year in range(2015,2017):
        for month in range(1,13):
            if year >= datetime.datetime.now().year:
                if month > datetime.datetime.now().month:
                    break

            userCountEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_GENERALUSER, month, year, StatisticsManager.BINNING_NONE)
            superCountEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT, str(month) + "/" + str(year % 1000), random.randrange(5, 15), StatisticsManager.SERIES_SUPERUSER, month, year, StatisticsManager.BINNING_NONE)
            adminCountEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT, str(month) + "/" + str(year % 1000), random.randrange(2, 6), StatisticsManager.SERIES_ADMINUSER, month, year, StatisticsManager.BINNING_NONE)
            accessesCardCountEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_ACCESSES, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_CARD_ACCESSES, month, year, StatisticsManager.BINNING_NONE)
            accessesWebCountEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_ACCESSES, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_WEB_ACCESSES, month, year, StatisticsManager.BINNING_NONE)
            loginsCountEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_LOGINS, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_SUCCESFULL_LOGINS, month, year, StatisticsManager.BINNING_NONE)
            failedLoginsCountEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_LOGINS, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_FAILED_LOGINS, month, year, StatisticsManager.BINNING_NONE)
            db.session.add(userCountEntry)
            db.session.add(superCountEntry)
            db.session.add(adminCountEntry)
            db.session.add(accessesCardCountEntry)
            db.session.add(accessesWebCountEntry)
            db.session.add(loginsCountEntry)
            db.session.add(failedLoginsCountEntry)


    for day in range(0,7):
        daynamesList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dayname = daynamesList[day]
        dayEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_WEEKDAYS,dayname,random.randrange(10,100), 0, 0, 0, day)
        db.session.add(dayEntry)

    for door in range(0,2):
        doorsnamesList = ["Kongs Door", "Rons Door"]
        doorname = doorsnamesList[door]
        doorEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_DOORS,doorname,random.randrange(10,100), 0, 0, 0, door)
        db.session.add(doorEntry)

    db.session.commit()

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
    db.session.add(Door(name = config.NODE_NAME, displayName = config.NODE_LOCAL_DOOR_NAME, address = 'http://localhost', keyMask = 0x03, local = 0x01, password= config.SYNC_MASTER_DEFAULT_PASSWORD))

    Setting.query.delete()
    db.session.add(Setting('NodeName', 'Test door', Setting.VALUETYPE_STRING))
    db.session.add(Setting('NodeValidKey','0x03', Setting.VALUETYPE_INT))

    Action.query.delete()
    db.session.add(Action(datetime.datetime.utcnow(), config.NODE_NAME, syncMasterUser.firstName + ' ' + syncMasterUser.lastName, syncMasterUser.email, 'Remove all data & regenerate database', 'Init systen', 'L1', 1, 'Internal'))

    db.session.commit()

if __name__ == '__main__':
    manager.run()

