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
import app.seed as seeder
import datetime
import random
import codecs
import sys

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

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
def open_the_door():
    "Force the local door openend"
    backgroundWorker.run()
    backgroundWorker.open_the_door()

@manager.command
def seed():
    "Seed RoseGuarden database filled default data after an migration/upgrade"
    seeder.seed()

@manager.command
def seed_statistic():
    "Create RoseGuarden database filled with testdata for the statistics"
    Statistic.query.delete()
    StatisticEntry.query.delete()

    userCountStat = Statistic("User total", StatisticsManager.STATISTICS_STATID_USERCOUNT, Statistic.STATTYPE_LINE_SERIES, 0, 3, "", 0, "Users", "Admins", "Supervisors")
    accessesStat = Statistic("Accesses total", StatisticsManager.STATISTICS_STATID_ACCESSES, Statistic.STATTYPE_LINE_SERIES, 0, 2, "", 0, "Card auth.", "Web auth.")
    weekdayStat = Statistic("Accesses per weekday", StatisticsManager.STATISTICS_STATID_WEEKDAYS, Statistic.STATTYPE_RADAR_SERIES, 7, 1, "", 0, "Weekdays")
    doorStat = Statistic("Accesses per node", StatisticsManager.STATISTICS_STATID_NODE_ACCESSES, Statistic.STATTYPE_DOUGHNUT_CLASSES, 2, 0, "", 0)
    loginsCountStat = Statistic("Logins", StatisticsManager.STATISTICS_STATID_LOGINS, Statistic.STATTYPE_LINE_SERIES, 0, 2, "", 0, "Logins", "Failed attempts")
    secuirityStat = Statistic("Security warnings", StatisticsManager.STATISTICS_STATID_SECURITY, Statistic.STATTYPE_LINE_SERIES, 0, 3, "", 0, "Failed login", "Failed API auth.", "Worker errors")
    activityGroupsStat = Statistic("User activity groups", StatisticsManager.STATISTICS_STATID_ACTIVITY_USER_GROUPS, Statistic.STATTYPE_YEARLY_BAR_SERIES, 0, 4, "", Statistic.STATDISPLAY_CONFIG_NO_TOTAL, "Zero activity users", "Low activity users", "Medium activity users", "High activity users")
    activityAccessesStat = Statistic("Average accesses of user groups", StatisticsManager.STATISTICS_STATID_USER_GROUPS_ACCESSES, Statistic.STATTYPE_LINE_SERIES, 0, 3, "",  Statistic.STATDISPLAY_CONFIG_NO_TOTAL, "Low activity users", "Medium activity users", "High activity users")
    activityAverageStat = Statistic("Total accesses of user groups", StatisticsManager.STATISTICS_STATID_USER_GROUPS_AVERAGE, Statistic.STATTYPE_YEARLY_BAR_SERIES, 0, 3, "", Statistic.STATDISPLAY_CONFIG_NO_TOTAL, "Low activity users", "Medium activity users", "High activity users")

    db.session.add(userCountStat)
    db.session.add(accessesStat)
    db.session.add(activityGroupsStat)
    db.session.add(activityAccessesStat)
    db.session.add(activityAverageStat)
    db.session.add(doorStat)
    db.session.add(loginsCountStat)
    db.session.add(weekdayStat)
    db.session.add(secuirityStat)

    # add entry for usercount
    for year in range(2015,2017):
        for month in range(1,13):
            if year >= datetime.datetime.now().year:
                if month > datetime.datetime.now().month:
                    break

            # STATISTICS_STATID_ACTIVITY_USER_GROUPS entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACTIVITY_USER_GROUPS, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_GROUPS_NO_ACTIVITY, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACTIVITY_USER_GROUPS, str(month) + "/" + str(year % 1000), random.randrange(5, 15), StatisticsManager.SERIES_GROUPS_LOW_ACTIVITY, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACTIVITY_USER_GROUPS, str(month) + "/" + str(year % 1000), random.randrange(2, 6), StatisticsManager.SERIES_GROUPS_MEDIUM_ACTIVITY, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACTIVITY_USER_GROUPS, str(month) + "/" + str(year % 1000), random.randrange(2, 6), StatisticsManager.SERIES_GROUPS_HIGH_ACTIVITY, month, year, StatisticsManager.BINNING_NONE))

            # STATISTICS_STATID_USER_GROUPS_ACCESSES entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_ACCESSES, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_GROUP_BY_LOW_ACTIVITY, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_ACCESSES, str(month) + "/" + str(year % 1000), random.randrange(5, 15), StatisticsManager.SERIES_GROUP_BY_MEDIUM_ACTIVITY, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_ACCESSES, str(month) + "/" + str(year % 1000), random.randrange(2, 6), StatisticsManager.SERIES_GROUP_BY_HIGH_ACTIVITY, month, year, StatisticsManager.BINNING_NONE))

            # STATISTICS_STATID_USER_GROUPS_ACCESSES entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_AVERAGE, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_GROUP_BY_LOW_ACTIVITY, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_AVERAGE, str(month) + "/" + str(year % 1000), random.randrange(5, 15), StatisticsManager.SERIES_GROUP_BY_MEDIUM_ACTIVITY, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_AVERAGE, str(month) + "/" + str(year % 1000), random.randrange(2, 6), StatisticsManager.SERIES_GROUP_BY_HIGH_ACTIVITY, month, year, StatisticsManager.BINNING_NONE))


            # STATISTICS_STATID_USERCOUNT entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_GENERALUSER, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT, str(month) + "/" + str(year % 1000), random.randrange(5, 15), StatisticsManager.SERIES_SUPERUSER, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT, str(month) + "/" + str(year % 1000), random.randrange(2, 6), StatisticsManager.SERIES_ADMINUSER, month, year, StatisticsManager.BINNING_NONE))
            # STATISTICS_STATID_ACCESSES entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACCESSES, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_CARD_ACCESSES, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACCESSES, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_WEB_ACCESSES, month, year, StatisticsManager.BINNING_NONE))
            # STATISTICS_STATID_LOGINS entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_LOGINS, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_SUCCESFULL_LOGINS, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_LOGINS, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_FAILED_LOGINS, month, year, StatisticsManager.BINNING_NONE))
            # STATISTICS_STATID_SECURITY entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_SECURITY, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_SECURITY_FAILED_LOGINS, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_SECURITY, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_SECURITY_FAILED_API_AUTH, month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_SECURITY, str(month) + "/" + str(year % 1000), random.randrange(20, 120), StatisticsManager.SERIES_SECURITY_WORKER_ERRORS, month, year, StatisticsManager.BINNING_NONE))

    for day in range(0,7):
        daynamesList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dayname = daynamesList[day]
        dayEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_WEEKDAYS,dayname,random.randrange(10,100), 0, 0, 0, day)
        db.session.add(dayEntry)

    for door in range(0,2):
        doorsnamesList = ["Elfe", "Duftwolke"]
        doorname = doorsnamesList[door]
        doorEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_NODE_ACCESSES,doorname,random.randrange(10,100), 0, 0, 0, door)
        db.session.add(doorEntry)

    db.session.commit()

@manager.command
def create_db():
    "Create RoseGuarden database"

    print "Create database (this will remove old data)"
    db.create_all()
    User.query.delete()

    # add syncmaster-user for synchronisation
    print "Add syncmaster user"
    syncMasterUser = User('syncmaster@roseguarden.org', SYNC_MASTER_DEFAULT_PASSWORD, 'Sync','Master',1)
    syncMasterUser.syncMaster = 1
    db.session.add(syncMasterUser)

    # you can add some default user here
    print "Add admin user"
    defaultUser1 = User('Administrator','pleasechangethepassword','RoseGuarden','Admin', 1)
    defaultUser1.accessType = 1
    db.session.add(defaultUser1)

    #db.session.add(Door(id = 0, name = 'front door', address = 'http://192.168.2.137', keyMask = 0x01, local = 0x00 ))
    #db.session.add(Door(id = 0, name = 'front door', address = 'http://192.168.2.138', keyMask = 0x01, local = 0x00 ))
    #db.session.add(Door(id = 0, name = 'front door', address = 'http://192.168.2.139', keyMask = 0x01, local = 0x00 ))

    print "Add local door"
    Door.query.delete()
    db.session.add(Door(name = config.NODE_NAME, displayName = 'Local', address = 'http://localhost', keyMask = 0x03, local = 0x01, password= config.SYNC_MASTER_DEFAULT_PASSWORD))

    print "Add default settings"
    Setting.query.delete()
    db.session.add(Setting('NODE_VALID_KEYS_MASK', '3', Setting.SETTINGTYPE_INT))


    print "Add log-entry"
    Action.query.delete()
    db.session.add(Action(datetime.datetime.utcnow(), config.NODE_NAME, syncMasterUser.firstName + ' ' + syncMasterUser.lastName, syncMasterUser.email, 'Remove all data & regenerate database', 'Init systen', 'L1', 1, 'Internal'))

    print "Save  new database"
    db.session.commit()

    print "Successfully create new database"

if __name__ == '__main__':
    manager.run()

