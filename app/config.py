import os
import logging


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    NAME = 'webservice'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MESSAGES_PER_PAGE = 10
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False

    @staticmethod
    def init_app(app):
        import sys
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(app.config['LOG_LEVEL'])
        app.logger.addHandler(handler)


class DevelopmentConfig(Config):
    ENV_NAME = os.environ.get('ENV_NAME') or 'dev'
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or logging.INFO
    LOGGER_NAME = ENV_NAME + '-' + Config.NAME
    # Database settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')


class ProductionConfig(Config):
    ENV_NAME = os.environ.get('ENV_NAME') or 'prod'
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or logging.INFO
    LOGGER_NAME = ENV_NAME + '-' + Config.NAME
    # Database settings
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')
    DB_PORT = os.environ.get('DB_PORT')

    # mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'\
        .format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME) 
        

class TestConfig(Config):
    ENV_NAME = 'test'
    LOG_LEVEL = logging.DEBUG
    LOGGER_NAME = ENV_NAME + '-' + Config.NAME
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    'DEV': DevelopmentConfig,
    'TEST': TestConfig,
    'PROD': ProductionConfig
}
