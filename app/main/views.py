#!/usr/bin/env python
# coding=utf-8

from . import main
from app import db, collect
from forms import ProfileForm
from flask import render_template, abort, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import User, Prototype
import requests


@main.route('/', methods=["GET"])
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


def get_article_from_search(str):
    page_content = requests.get("http://so.gushiwen.org/search.aspx?value="+str).content
    return collect.parse_search_result(page_content)


@main.route('/search', methods=["GET", "POST"])
def search():
    form_data = request.form.get("content", default=None)
    if form_data is None:
        abort(404)
    articles = get_article_from_search(form_data)
    if articles is None:
        abort(404)
    return render_template("search_result.html", articles=articles)

