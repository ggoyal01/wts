import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
                              'sqlite:///' + os.path.join(basedir, 'wts.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIN_BAL = float(os.environ.get('MIN_BAL'))
    RETRIES_ON_DB_LOCK = int(os.environ.get('RETRIES_ON_DB_LOCK'))
