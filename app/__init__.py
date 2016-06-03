#!/usr/bin/env python

"""
This the application initialization model.
"""
from flask import Flask
from flask_bootstrap import Bootstrap
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


bootstrap = Bootstrap()
db = SQLAlchemy()
lm = LoginManager()
lm.session_protection = "strong"
lm.login_view = "auth.login"


def create_app(config_name):
    """this method to create an application that inherit from Flask
    :return: an instance of app
    :param config_name: """

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    bootstrap.init_app(app)
    db.init_app(app)
    lm.init_app(app)

    return app
