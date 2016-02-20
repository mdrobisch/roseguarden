__author__ = 'drobisch'

import datetime
import config
import helpers
from models import User, Action, Door, RfidTagInfo, Statistic, StatisticEntry
from server import db

class StatisticsManager(object):

    # Monthly stats.
    STATISTICS_STATID_USERCOUNT    =   1
    STATISTICS_STATID_ACCESSES     =   2
    STATISTICS_STATID_AUTH_CARDS   =   3
    STATISTICS_STATID_WEB_CLIENT   =   4
    STATISTICS_STATID_DOORS        =   5
    STATISTICS_STATID_WEEKDAYS     =   6
    STATISTICS_STATID_LOGINS       =   7

    BINNING_NONE = 0

    SERIES_NONE = 0
    SERIES_GENERALUSER = 0
    SERIES_SUPERUSER = 1
    SERIES_ADMINUSER = 2

    SERIES_CARD_ACCESSES = 0
    SERIES_WEB_ACCESSES = 1

    SERIES_SUCCESFULL_LOGINS = 0
    SERIES_FAILED_LOGINS = 1

    @staticmethod
    def updateUserCountStat():
        print "userCount stat"

    @staticmethod
    def raiseUserCountChangedEvent():
        print "raise Usercount change"
        stat = Statistic.query.filter(Statistic.statId == StatisticsManager.STATISTICS_STATID_USERCOUNT).first()
        if stat == None:
            newStat = Statistic("User count", StatisticsManager.STATISTICS_STATID_USERCOUNT, Statistic.STATTYPE_LINE_SERIES, 0, 3, "Users", "Admins", "Supervisors")
            db.session.add(newStat)
            db.session.commit()
            print "statistic not present"

        userCount = helpers.get_query_count(User.query.filter(User.syncMaster == 0).filter(User.role == 0))
        adminCount = helpers.get_query_count(User.query.filter(User.syncMaster == 0).filter(User.role == 1))
        supervisorCount = helpers.get_query_count(User.query.filter(User.syncMaster == 0).filter(User.role == 2))

        currentMonth = datetime.datetime.now().month
        currentYear = int(datetime.datetime.now().year) % 100
        currentStatEntry = StatisticEntry.query.filter(StatisticEntry.month == currentMonth).all()

        if currentStatEntry == []:
            newStatEntryUsers = StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT,str(currentMonth) + '/' + str(currentYear), userCount, 0, currentMonth, currentYear, 0)
            newStatEntrySupervisors = StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT,str(currentMonth) + '/' + str(currentYear), supervisorCount, 1, currentMonth,currentYear,0)
            newStatEntryAdmins = StatisticEntry(StatisticsManager.STATISTICS_STATID_USERCOUNT,str(currentMonth) + '/' + str(currentYear), adminCount, 2, currentMonth, currentYear, 0)
            try:
                db.session.add(newStatEntryUsers)
                db.session.add(newStatEntrySupervisors)
                db.session.add(newStatEntryAdmins)
                db.session.commit()
            except:
                db.session.rollback()
                raise

    @staticmethod
    def raiseAccessEvent(authType):
        print "raise Usercount change"
        stat = Statistic.query.filter(Statistic.statId == StatisticsManager.STATISTICS_STATID_ACCESSES).first()
        if stat == None:
            newStat = Statistic("Access count", StatisticsManager.STATISTICS_STATID_ACCESSES, Statistic.STATTYPE_LINE_SERIES, 0, 3, "Card based", "Web based")
            db.session.add(newStat)
            db.session.commit()
            print "statistic not present"

        userCount = helpers.get_query_count(User.query.filter(User.syncMaster == 0).filter(User.role == 0))
        adminCount = helpers.get_query_count(User.query.filter(User.syncMaster == 0).filter(User.role == 1))
        supervisorCount = helpers.get_query_count(User.query.filter(User.syncMaster == 0).filter(User.role == 2))

        currentMonth = datetime.datetime.now().month
        currentYear = int(datetime.datetime.now().year) % 100
        currentStatEntry = StatisticEntry.query.filter(StatisticEntry.month == currentMonth).all()

        if currentStatEntry == []:
            newStatEntryCard = StatisticEntry(StatisticsManager.STATISTICS_STATID_ACCESSES,str(currentMonth) + '/' + str(currentYear), 0, 0, currentMonth, currentYear, 0)
            newStatEntryWeb = StatisticEntry(StatisticsManager.STATISTICS_STATID_ACCESSES,str(currentMonth) + '/' + str(currentYear), 0, 1, currentMonth,currentYear,0)
            try:
                db.session.add(newStatEntryCard)
                db.session.add(newStatEntryWeb)
                db.session.commit()
            except:
                db.session.rollback()
                raise

        entry = None
        if authType == User.AUTHTYPE_RFID:
            entry = StatisticEntry.query.filter(StatisticEntry.statId == StatisticsManager.STATISTICS_STATID_ACCESSES).filter(StatisticEntry.series == 0).first()
        if authType == User.AUTHTYPE_WEB:
            entry = StatisticEntry.query.filter(StatisticEntry.statId == StatisticsManager.STATISTICS_STATID_ACCESSES).filter(StatisticEntry.series == 1).first()
        if entry is not None:
            entry.value =  entry.value + 1
            db.session.commit()

    @staticmethod
    def raiseAuthCardsEvent(statId):
        print "raise Usercount"


    @staticmethod
    def raiseEvent(statId):
        print "Raise event"
        StatisticsManager.raiseAccessEvent(User.AUTHTYPE_WEB)
        #user = User.query.filter_by(id=id).first()
        #logentry = Action(datetime.datetime.utcnow(), config.NODE_NAME, g.user.firstName + ' ' + g.user.lastName,
        #               g.user.email, 'Invalidate auth. card of ' + user.firstName + ' ' + user.lastName + ' (' + user.email + ')',
        #               'Invalidate lost auth. card', 'L2', 0, 'Web based', Action.ACTION_OPENING_REQUEST)

