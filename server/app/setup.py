from server import db
from server import app as flask
from models import User, Action, NodeLink, Setting, Statistic, StatisticEntry
from statistics import StatisticsManager
from config import ConfigManager
from Queue import Queue
from threading import Thread
import time
import random
import datetime
import collections


setupStatusQueue = Queue()

SetupRunning = False
SetupLog = collections.namedtuple('SetupLog', ('progress', 'date', 'message', 'error'))

def seed_statistic():
    setupStatusQueue.put(
        SetupLog(progress=90, date=datetime.datetime.now().isoformat(), message='Statistic entries initialized ...', error=False))


    Statistic.query.delete()
    StatisticEntry.query.delete()

    userCountStat = Statistic("User total", StatisticsManager.STATISTICS_STATID_USERCOUNT, Statistic.STATTYPE_LINE_SERIES,
                              0, 3, "", 0, "Users", "Admins", "Supervisors")
    accessesStat = Statistic("Accesses total", StatisticsManager.STATISTICS_STATID_ACCESSES, Statistic.STATTYPE_LINE_SERIES,
                             0, 2, "", 0, "Card auth.", "Web auth.")
    weekdayStat = Statistic("Accesses per weekday", StatisticsManager.STATISTICS_STATID_WEEKDAYS,
                            Statistic.STATTYPE_RADAR_SERIES, 7, 1, "", 0, "Weekdays")
    doorStat = Statistic("Accesses per node", StatisticsManager.STATISTICS_STATID_NODE_ACCESSES,
                         Statistic.STATTYPE_DOUGHNUT_CLASSES, 2, 0, "", 0)
    loginsCountStat = Statistic("Logins", StatisticsManager.STATISTICS_STATID_LOGINS, Statistic.STATTYPE_LINE_SERIES, 0, 2,
                                "", 0, "Logins", "Failed attempts")
    secuirityStat = Statistic("Security warnings", StatisticsManager.STATISTICS_STATID_SECURITY,
                              Statistic.STATTYPE_LINE_SERIES, 0, 3, "", 0, "Failed login", "Failed API auth.",
                              "Worker errors")
    activityGroupsStat = Statistic("User activity groups", StatisticsManager.STATISTICS_STATID_ACTIVITY_USER_GROUPS,
                                   Statistic.STATTYPE_YEARLY_BAR_SERIES, 0, 4, "", Statistic.STATDISPLAY_CONFIG_NO_TOTAL,
                                   "Zero activity users", "Low activity users", "Medium activity users",
                                   "High activity users")
    activityAccessesStat = Statistic("Average accesses of user groups",
                                     StatisticsManager.STATISTICS_STATID_USER_GROUPS_ACCESSES,
                                     Statistic.STATTYPE_LINE_SERIES, 0, 3, "", Statistic.STATDISPLAY_CONFIG_NO_TOTAL,
                                     "Low activity users", "Medium activity users", "High activity users")
    activityAverageStat = Statistic("Total accesses of user groups",
                                    StatisticsManager.STATISTICS_STATID_USER_GROUPS_AVERAGE,
                                    Statistic.STATTYPE_YEARLY_BAR_SERIES, 0, 3, "", Statistic.STATDISPLAY_CONFIG_NO_TOTAL,
                                    "Low activity users", "Medium activity users", "High activity users")

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
    for year in range(2015, 2017):
        for month in range(1, 13):
            if year >= datetime.datetime.now().year:
                if month > datetime.datetime.now().month:
                    break

            # STATISTICS_STATID_ACTIVITY_USER_GROUPS entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACTIVITY_USER_GROUPS,
                                          str(month) + "/" + str(year % 1000), random.randrange(20, 120),
                                          StatisticsManager.SERIES_GROUPS_NO_ACTIVITY, month, year,
                                          StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACTIVITY_USER_GROUPS,
                                          str(month) + "/" + str(year % 1000), random.randrange(5, 15),
                                          StatisticsManager.SERIES_GROUPS_LOW_ACTIVITY, month, year,
                                          StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACTIVITY_USER_GROUPS,
                                          str(month) + "/" + str(year % 1000), random.randrange(2, 6),
                                          StatisticsManager.SERIES_GROUPS_MEDIUM_ACTIVITY, month, year,
                                          StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACTIVITY_USER_GROUPS,
                                          str(month) + "/" + str(year % 1000), random.randrange(2, 6),
                                          StatisticsManager.SERIES_GROUPS_HIGH_ACTIVITY, month, year,
                                          StatisticsManager.BINNING_NONE))

            # STATISTICS_STATID_USER_GROUPS_ACCESSES entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_ACCESSES,
                                          str(month) + "/" + str(year % 1000), random.randrange(20, 120),
                                          StatisticsManager.SERIES_GROUP_BY_LOW_ACTIVITY, month, year,
                                          StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_ACCESSES,
                                          str(month) + "/" + str(year % 1000), random.randrange(5, 15),
                                          StatisticsManager.SERIES_GROUP_BY_MEDIUM_ACTIVITY, month, year,
                                          StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_ACCESSES,
                                          str(month) + "/" + str(year % 1000), random.randrange(2, 6),
                                          StatisticsManager.SERIES_GROUP_BY_HIGH_ACTIVITY, month, year,
                                          StatisticsManager.BINNING_NONE))

            # STATISTICS_STATID_USER_GROUPS_ACCESSES entries
            db.session.add(
                StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_AVERAGE, str(month) + "/" + str(year % 1000),
                               random.randrange(20, 120), StatisticsManager.SERIES_GROUP_BY_LOW_ACTIVITY, month, year,
                               StatisticsManager.BINNING_NONE))
            db.session.add(
                StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_AVERAGE, str(month) + "/" + str(year % 1000),
                               random.randrange(5, 15), StatisticsManager.SERIES_GROUP_BY_MEDIUM_ACTIVITY, month, year,
                               StatisticsManager.BINNING_NONE))
            db.session.add(
                StatisticEntry(StatisticsManager.STATISTICS_STATID_USER_GROUPS_AVERAGE, str(month) + "/" + str(year % 1000),
                               random.randrange(2, 6), StatisticsManager.SERIES_GROUP_BY_HIGH_ACTIVITY, month, year,
                               StatisticsManager.BINNING_NONE))

            # STATISTICS_STATID_USERCOUNT entries
            db.session.add(
                StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT, str(month) + "/" + str(year % 1000),
                               random.randrange(20, 120), StatisticsManager.SERIES_GENERALUSER, month, year,
                               StatisticsManager.BINNING_NONE))
            db.session.add(
                StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT, str(month) + "/" + str(year % 1000),
                               random.randrange(5, 15), StatisticsManager.SERIES_SUPERUSER, month, year,
                               StatisticsManager.BINNING_NONE))
            db.session.add(
                StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT, str(month) + "/" + str(year % 1000),
                               random.randrange(2, 6), StatisticsManager.SERIES_ADMINUSER, month, year,
                               StatisticsManager.BINNING_NONE))
            # STATISTICS_STATID_ACCESSES entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACCESSES, str(month) + "/" + str(year % 1000),
                                          random.randrange(20, 120), StatisticsManager.SERIES_CARD_ACCESSES, month, year,
                                          StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_ACCESSES, str(month) + "/" + str(year % 1000),
                                          random.randrange(20, 120), StatisticsManager.SERIES_WEB_ACCESSES, month, year,
                                          StatisticsManager.BINNING_NONE))
            # STATISTICS_STATID_LOGINS entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_LOGINS, str(month) + "/" + str(year % 1000),
                                          random.randrange(20, 120), StatisticsManager.SERIES_SUCCESFULL_LOGINS, month,
                                          year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_LOGINS, str(month) + "/" + str(year % 1000),
                                          random.randrange(20, 120), StatisticsManager.SERIES_FAILED_LOGINS, month, year,
                                          StatisticsManager.BINNING_NONE))
            # STATISTICS_STATID_SECURITY entries
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_SECURITY, str(month) + "/" + str(year % 1000),
                                          random.randrange(20, 120), StatisticsManager.SERIES_SECURITY_FAILED_LOGINS, month,
                                          year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_SECURITY, str(month) + "/" + str(year % 1000),
                                          random.randrange(20, 120), StatisticsManager.SERIES_SECURITY_FAILED_API_AUTH,
                                          month, year, StatisticsManager.BINNING_NONE))
            db.session.add(StatisticEntry(StatisticsManager.STATISTICS_STATID_SECURITY, str(month) + "/" + str(year % 1000),
                                          random.randrange(20, 120), StatisticsManager.SERIES_SECURITY_WORKER_ERRORS, month,
                                          year, StatisticsManager.BINNING_NONE))

    for day in range(0, 7):
        daynamesList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dayname = daynamesList[day]
        dayEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_WEEKDAYS, dayname, random.randrange(10, 100), 0, 0, 0,
                                  day)
        db.session.add(dayEntry)

    for door in range(0, 2):
        doorsnamesList = ["Elfe", "Duftwolke"]
        doorname = doorsnamesList[door]
        doorEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_NODE_ACCESSES, doorname, random.randrange(10, 100),
                                   0, 0, 0, door)
        db.session.add(doorEntry)

    db.session.commit()


def create_db():
    "Create RoseGuarden database"
    print "Create database (this will remove old data)"

    db.create_all()
    setupStatusQueue.put(
        SetupLog(progress=10, date=datetime.datetime.now().isoformat(), message='Database created ...', error=False))

    User.query.delete()
    print "Add syncmaster user"
    syncMasterUser = User('syncmaster@roseguarden.org', ConfigManager.INITIAL_NODE_PASSWORD, 'Sync', 'Master', 1)
    syncMasterUser.syncMaster = 1
    db.session.add(syncMasterUser)

    setupStatusQueue.put(
        SetupLog(progress=20, date=datetime.datetime.now().isoformat(), message='Synchronisation-user created ...',
                 error=False))

    print "Add admin user ", ConfigManager.INITIAL_NODE_PASSWORD
    defaultUser1 = User('Administrator', ConfigManager.INITIAL_NODE_PASSWORD, 'RoseGuarden', 'Admin', 1)
    defaultUser1.accessType = 1
    db.session.add(defaultUser1)

    setupStatusQueue.put(
        SetupLog(progress=40, date=datetime.datetime.now().isoformat(), message='Admin-user created ...', error=False))

    # you can add some default user here

    # db.session.add(Door(id = 0, name = 'front door', address = 'http://192.168.2.137', keyMask = 0x01, local = 0x00 ))
    # db.session.add(Door(id = 0, name = 'front door', address = 'http://192.168.2.138', keyMask = 0x01, local = 0x00 ))
    # db.session.add(Door(id = 0, name = 'front door', address = 'http://192.168.2.139', keyMask = 0x01, local = 0x00 ))

    print "Add local door"
    NodeLink.query.delete()
    db.session.add(
        NodeLink(name=ConfigManager.NODE_NAME, displayName='Local', address='http://localhost', keyMask=0x03, local=0x01,
                 password=ConfigManager.INITIAL_NODE_PASSWORD))

    setupStatusQueue.put(
        SetupLog(progress=60, date=datetime.datetime.now().isoformat(), message='Local door added ...', error=False))

    print "Add default settings"
    Setting.query.delete()
    db.session.add(Setting('NODE_VALID_KEYS_MASK', '3', Setting.SETTINGTYPE_INT))

    print "Add log-entry"
    Action.query.delete()
    db.session.add(
        Action(datetime.datetime.utcnow(), ConfigManager.NODE_NAME, syncMasterUser.firstName + ' ' + syncMasterUser.lastName,
               syncMasterUser.email, 'Remove all data & regenerate database', 'Init systen', 'L1', 1, 'Internal'))

    setupStatusQueue.put(
        SetupLog(progress=70, date=datetime.datetime.now().isoformat(), message='Logging system initialized ...',
                 error=False))

    print "Save  new database"
    db.session.commit()

    setupStatusQueue.put(
        SetupLog(progress=80, date=datetime.datetime.now().isoformat(), message='Database-data saved ...', error=False))



def setupThread(statusQueue):
    global SetupRunning
    SetupRunning = True

    print "Setup started"
    setupStatusQueue.put(
        SetupLog(progress=0, date=datetime.datetime.now().isoformat(), message='Setup started ...', error=False))

    create_db()
    seed_statistic()

    print "Successfully create new database"
    setupStatusQueue.put(
        SetupLog(progress=100, date=datetime.datetime.now().isoformat(), message='Setup finished ...', error=False))

    SetupRunning = False

def lock():
    with open('config.lock', "w+"):
        pass
    ConfigManager.reloadConfig()
    flask.static_folder = '../extensions/' + ConfigManager.EXTENSION_NAME + '/frontend'

def startSetup():
    worker = Thread(target=setupThread, args=(setupStatusQueue,))
    worker.setDaemon(True)
    worker.start()
