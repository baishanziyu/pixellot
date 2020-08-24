import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'mysql://pixellot:pixellot@52.82.60.3:3306/pixellot'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_POOL_SIZE = 1024
    SQLALCHEMY_POOL_TIMEOUT = 90
    SQLALCHEMY_POOL_RECYCLE = 3
    SQLALCHEMY_MAX_OVERFLOW = 1024
    SQLALCHEMY_COMMIT_TEARDOWN = True
    @staticmethod
    def init_app(app):
        pass

config = {
    'default': Config
}
