#!venv/bin/python
# coding=utf-8

import os

from app import create_app, db
from app.models import User, Role, Prototype
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from werkzeug.contrib.fixers import ProxyFix

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
app.wsgi_app = ProxyFix(app.wsgi_app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Prototype=Prototype)

if __name__ == "__main__":
    manager.add_command("shell", Shell(make_context=make_shell_context))
    manager.run()
