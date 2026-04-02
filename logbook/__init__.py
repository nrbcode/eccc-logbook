# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

#import psycopg2
from dotenv import load_dotenv
from importlib import import_module

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


load_dotenv()

db = SQLAlchemy()
bc = Bcrypt()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'activity'):
        module = import_module('logbook.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    if not app.config.get('DATABASE_URL'):
        # local database
        with app.app_context():
            db.create_all()
    else:
        # remote database
        """
        import logbook.database as ldb
        connection = psycopg2.connect(app.config.get('SQLALCHEMY_DATABASE_URI'))
        ldb.create_tables(connection)
        """
        #from logbook.authentication.models import User
        with app.app_context():
            db.create_all()
    
    
def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)    
    configure_database(app)

    return app
