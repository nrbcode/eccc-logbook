# -*- encoding: utf-8 -*-
"""
Configuration and settings
"""

import os, secrets

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')
    
    # Set up the App secret key
    SECRET_KEY  = os.getenv('FLASK_SECRET_KEY', secrets.token_hex())
    
    # Configure the textual database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_URL    = os.getenv("DATABASE_URL")
    DB_ENGINE       = os.getenv('DB_ENGINE')
    DB_USERNAME     = os.getenv('DB_USERNAME')
    DB_PASS         = os.getenv('DB_PASS')
    DB_HOST         = os.getenv('DB_HOST')
    DB_PORT         = os.getenv('DB_PORT')
    DB_NAME         = os.getenv('DB_NAME')

    # try to set up a Relational DBMS
    if not DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Email server credentials
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'SafetyBase Admin <Admin@safetybase-aus.info>')
    RESEND_API_KEY      = os.getenv('RESEND_API_KEY')

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

class DebugConfig(Config):
    DEBUG = True

# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
