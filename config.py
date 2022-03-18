import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir, 'todo.sqlite')

# Turn off the Flask-SQLAlchemy event system and warning
SQLALCHEMY_TRACK_MODIFICATIONS = False

SESSION_TYPE = 'filesystem'

SECRET_KEY = os.urandom(32)

# Mail configs
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "testmahnoor@gmail.com"
MAIL_PASSWORD = "abcd.1234"
MAIL_DEFAULT_SENDER = 'testmahnoor@gmail.com'
