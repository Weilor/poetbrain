#!/usr/bin/env python
# encoding = utf-8

from . import main
from app import db
from forms import ProfileForm
from flask import render_template, abort, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Prototype


@main.route('/')
def index():
    prototypes = Prototype.query.all()
    return render_template("index.html", prototypes=prototypes)


@main.route('/user/<username>')
def user_page(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    return render_template("user_page.html", user=user)


@main.route('/modify_profile', methods=['GET', 'POST'])
@login_required
def modify_profile():
    if not current_user.confirmed:
        return render_template('auth/user_confirm.html', confirmed=False)
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        return redirect(url_for("main.user_page", username=current_user.username))
    form.about_me.data = current_user.about_me
    form.location.data = current_user.location
    return render_template('modify_profile.html', form=form, user=current_user)
