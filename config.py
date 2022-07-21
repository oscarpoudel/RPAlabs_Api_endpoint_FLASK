# set the config file for different situation
# and import config as python object

class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = 'test key'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///database///vid.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 1024*1024*1024

    UPLOAD_FOLDER = 'app\\static\\uploads'
    ALLOWED_EXTENSIONS = set(['mkv', 'mp4'])
    ALLOWED_DURATION = 10  # in minutes


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
