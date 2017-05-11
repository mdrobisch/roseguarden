__author__ = 'drobisch'
from models import User, Action, NodeLink, RfidTagInfo, Statistic, StatisticEntry
from server import db


def seed():
    stats = Statistic.query.all()
    if stats is not None:
        for stat in stats:
            print stat.description
            if stat.description == 0:
                print "seed description"
                stat.description = ""
            if stat.displayConfig is None:
                print "seed displayConfig"
                stat.displayConfig = 0
        db.session.commit()
