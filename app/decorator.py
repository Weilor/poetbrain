#!/usr/bin/env python
# coding=utf-8

from functools import wraps
from flask_login import current_user
from flask import abort
from app.models import Permission


def permission_required(permission):
    def wrapper(f):
        @wraps(f)
        def decorated_f(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_f
    return wrapper


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
