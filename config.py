# config.py
import os

class Config(object):
    """
    Common configurations
    """

    # Put any configurations here that are common across all environments
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'alphagammawebmaster@gmail.com'
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    SECURITY_PASSWORD_SALT = 'alpha_gamma_bitch'

class DevelopmentConfig(Config):
    """
    Development configurations
    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}