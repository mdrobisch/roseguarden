__author__ = 'drobisch'
import app.config as config
from app.server import app, db
from app.worker import backgroundWorker
from flask_script import Manager, Option
from flask_migrate import MigrateCommand
from flask_alchemydumps import AlchemyDumpsCommand
import app.setup  as setup
import app.seed as seeder
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
    app.run('0.0.0.0', port=80, threaded=True)

    # after exiting the app, cancel the backgroundowrker
    backgroundWorker.cancel()

@manager.command
def seed():
    "Seed RoseGuarden database filled default data after an migration/upgrade"
    seeder.seed()

@manager.command
def unittests():
    "Test the server-functionality"
    from app.security import securityTests
    securityTests()

@manager.command
def seed_statistic():
    "Create RoseGuarden database filled with testdata for the statistics"
    setup.seed_statistic()

@manager.command
def create_db():
    "Create RoseGuarden database"
    setup.create_db()

if __name__ == '__main__':
    manager.run()

