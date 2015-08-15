__author__ = 'drobisch'
from app.server import app, db
from app.worker import backgroundWorker
from app.test import test_envirment


test_envirment()

# start backgroundworker
backgroundWorker.run()

# running the flask app
#app.run('0.0.0.0')
app.run()

# after exiting the app, cancel the backgroundowrker
backgroundWorker.cancel()
