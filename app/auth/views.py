#!/usr/bin/env python
# encoding = utf-8

from . import auth
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from forms import LoginForm, SignupForm
from app.models import User, db
from app.email import send_mail
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


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
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash("Login failed!")
    return render_template("auth/login.html", form=form)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have logout successful.")
    return redirect(url_for('main.index'))


@auth.route('/signup', methods=['GET', 'POST'])
def user_signup():
    form = SignupForm()
    if form.validate_on_submit():
        password = form.password.data
        user = User(email=form.email.data, username=form.name.data, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        token = user.generate_token()
        send_mail(to=user.email, subject="Confirm Your Account", template='auth/email/confirm', token=token, user=user)
        flash("Register successful.Pleas log in.And a confirm message has been sent to your email.")
        user.member_since = datetime.utcnow()
        return redirect(request.args.get('next') or url_for('auth.login'))
    return render_template("auth/user_signup.html", form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    elif current_user.check_token(token):
        confirmed = True
    else:
        confirmed = False
    return render_template('auth/user_confirm.html', confirmed=confirmed)


@auth.route('/reconfirm', methods=['GET'])
@login_required
def user_reconfirm():
    if current_user.confirmed:
        return render_template('auth/user_confirm.html', confirmed=True)
    else:
        token = current_user.generate_token()
        send_mail(to=current_user.email, subject="Confirm Your Account", template='auth/email/confirm',
                  token=token, user=current_user)
        flash("Register successful.Pleas log in.And a confirm message has been sent to your email.")
        return redirect(request.args.get('next') or url_for('auth.login'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != "auth.":
            return render_template("auth/user_confirm.html", confirmed=False)

