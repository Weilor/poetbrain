#!/usr/bin/env python

"""
This the application initialization model.
"""
from flask import Flask
from flask_bootstrap import Bootstrap


bootstrap = Bootstrap()


def create_app():
    """this method to create an application that inherit from Flask
    input: config name
    return: an instance of app"""

    app = Flask(__name__)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    bootstrap.init_app(app)

    return app
