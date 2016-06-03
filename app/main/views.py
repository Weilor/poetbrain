#!/usr/bin/env python

from . import main
from app import db
from app.models import User
from werkzeug.security import generate_password_hash
from .forms import SignupForm
from flask import render_template, flash


@main.route('/')
def index():
    return render_template("index.html")


@main.route('/user/<username>')
def user_page(username):
    return render_template("user_page.html", name=username)


@main.route('/signup')
def user_signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        user = User.query.filter_by(username=name).first()
        if user is not None:
            flash("The username is exist already.Please try another username.")
        else:
            db.session.add(User(username=name, password_hash=generate_password_hash(password)))
    return render_template("user_signup.html", form=form)

