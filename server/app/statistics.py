__author__ = 'drobisch'

import datetime
import config
import helpers
from models import User, Action, Door, RfidTagInfo, Statistic, StatisticEntry
from server import db
import random

class StatisticsManager(object):

    # Monthly stats.
    STATISTICS_STATID_USERCOUNT     =   1
    STATISTICS_STATID_ACCESSES      =   2
    STATISTICS_STATID_AUTH_CARDS    =   3
    STATISTICS_STATID_WEB_CLIENT    =   4
    STATISTICS_STATID_NODE_ACCESSES =   5
    STATISTICS_STATID_WEEKDAYS      =   6
    STATISTICS_STATID_LOGINS        =   7
    STATISTICS_STATID_SECURITY      =   8

    BINNING_NONE = 0

    SERIES_NONE = 0

    SERIES_GENERALUSER = 0
    SERIES_SUPERUSER = 1
    SERIES_ADMINUSER = 2

    SERIES_CARD_ACCESSES = 0
    SERIES_WEB_ACCESSES = 1

    SERIES_SUCCESFULL_LOGINS = 0
    SERIES_FAILED_LOGINS = 1

    SERIES_SECURITY_FAILED_LOGINS = 0
    SERIES_SECURITY_FAILED_API_AUTH = 1
    SERIES_SECURITY_WORKER_ERRORS = 2

    @staticmethod
    def staticEntryAddOrUpdate(statTye, statId, label, value, month, year, binningId, series):
        statEntry = StatisticEntry.query.filter_by(statId = statId, label = label,series = series, month = month, year = year).first()
        if statEntry is None:
            newEntry = StatisticEntry(statId, label, value, series, month, year, binningId)
            db.session.add(newEntry)
        else:
            statEntry.value = value
        db.session.commit()

    @staticmethod
    def incrementalEntryAddOrUpdate(statTye, statId, label, value, month, year, binningId, series):
        statEntry = StatisticEntry.query.filter_by(statId = statId, label = label,series = series, month = month, year = year).first()
        if statEntry is None:
            newEntry = StatisticEntry(statId, label, value, series, month, year, binningId)
            db.session.add(newEntry)
        else:
            statEntry.value += value
        db.session.commit()

    @staticmethod
    def updateUserCountStat(updateData):
        print "Update UserCount stat"
        stat = Statistic.query.filter(Statistic.statId == StatisticsManager.STATISTICS_STATID_USERCOUNT).first()
        if stat == None:
            newStat = Statistic("User total", StatisticsManager.STATISTICS_STATID_USERCOUNT, Statistic.STATTYPE_LINE_SERIES, 0, 3, "Users", "Supervisors", "Admins")
            db.session.add(newStat)
            db.session.commit()

        now = datetime.datetime.now() #- datetime.timedelta(days=30)
        month = now.month
        year = now.year
        for i in range(0, 3):
            StatisticsManager.staticEntryAddOrUpdate(Statistic.STATTYPE_LINE_SERIES, StatisticsManager.STATISTICS_STATID_USERCOUNT, str(month) + "/" + str(year % 1000), updateData[i], month, year, StatisticsManager.BINNING_NONE, i)


    @staticmethod
    def updateAccessesStat(updateData):
        print "Update Accesses stat"
        stat = Statistic.query.filter(Statistic.statId == StatisticsManager.STATISTICS_STATID_ACCESSES).first()
        if stat == None:
            newStat = Statistic("Accesses total", StatisticsManager.STATISTICS_STATID_ACCESSES, Statistic.STATTYPE_LINE_SERIES, 0, 2, "Card auth.", "Web auth.")
            db.session.add(newStat)
            db.session.commit()

        for year in updateData:
            for month in updateData[year]:
                for seriesIndex in range(len(updateData[year][month])):
                    StatisticsManager.incrementalEntryAddOrUpdate(Statistic.STATTYPE_LINE_SERIES, StatisticsManager.STATISTICS_STATID_ACCESSES, str(month) + "/" + str(year % 1000), updateData[year][month][seriesIndex], month, year, StatisticsManager.BINNING_NONE, seriesIndex)

    @staticmethod
    def updateWeekdaysStat(updateData):
        print "Update Weekdate stat"
        stat = Statistic.query.filter(Statistic.statId == StatisticsManager.STATISTICS_STATID_WEEKDAYS).first()
        if stat == None:
            newStat = Statistic("Accesses per weekday", StatisticsManager.STATISTICS_STATID_WEEKDAYS, Statistic.STATTYPE_RADAR_SERIES, 7, 1, "Weekdays")
            db.session.add(newStat)
            db.session.commit()

        for day in range(0,7):
            daynamesList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            dayname = daynamesList[day]
            #dayEntry = StatisticEntry(StatisticsManager.STATISTICS_STATID_WEEKDAYS,dayname,random.randrange(10,100), 0, 0, 0, day)
            StatisticsManager.incrementalEntryAddOrUpdate(Statistic.STATTYPE_RADAR_SERIES,StatisticsManager.STATISTICS_STATID_WEEKDAYS,dayname,updateData[day], 0, 0, day, 0)

    @staticmethod
    def updateNodeAccessStat(updateData):
        print "Update node accesses stat"
        stat = Statistic.query.filter(Statistic.statId == StatisticsManager.STATISTICS_STATID_NODE_ACCESSES).first()
        if stat == None:
            newStat = Statistic("Accesses per node", StatisticsManager.STATISTICS_STATID_NODE_ACCESSES, Statistic.STATTYPE_DOUGHNUT_CLASSES, 0, 0)
            db.session.add(newStat)
            db.session.commit()

        for nodeName in updateData:
            StatisticsManager.incrementalEntryAddOrUpdate(Statistic.STATTYPE_DOUGHNUT_CLASSES, StatisticsManager.STATISTICS_STATID_NODE_ACCESSES,nodeName,updateData[nodeName],0,0,0,0)

    @staticmethod
    def updateLoginStat():
        print "Update Login stat"

    @staticmethod
    def updateSecurityStat():
        print "Update Security stat"

