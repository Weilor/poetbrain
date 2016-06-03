#!/usr/bin/env python

from . import auth
from flask import render_template, flash
from flask_login import login_user
from forms import LoginForm
from app.models import User
from werkzeug.security import check_password_hash


@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.user_name.data
        password = form.password.data
        user = User.query.filter_by(username=name).first()
        if user is None:
            flash("The username is not exist .Please check username.")
        elif check_password_hash(user.password_hash, password):
            flash("Login successful!")
            login_user(user, form.remember_me.data)
        else:
            flash("Login failed!")
    return render_template("auth/login.html", form=form)
