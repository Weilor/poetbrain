#!/usr/bin/env python
# coding=utf-8

from . import main
from app import db, collect
from forms import ProfileForm, MementoForm
from flask import render_template, abort, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import User, Prototype
from app.decorator import admin_required
import requests
import re


@main.route('/', methods=["GET"])
def index():
    prototypes = Prototype.query.all()
    for prototype in prototypes:
        prototype.body = put_linesep_in(prototype.body)
        print prototype.body
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


def get_article_from_search(data):
    articles = []
    page_content = requests.get("http://so.gushiwen.org/search.aspx?value="+data).content
    while page_content is not None:
        articles += (collect.parse_search_result(page_content))
        result = re.search('(/search.*)">下一页', page_content)
        if result is not None:
            page_content = requests.get("http://so.gushiwen.org" + result.groups()[0]).content
        else:
            break
    return articles


def get_article_from_db(author_or_title):
    articles = Prototype.is_prototype_exist(author_or_title)
    return articles


@main.route('/search', methods=["GET", "POST"])
def search():
    form_data = request.form.get("content", default=None)
    if form_data is None:
        abort(404)
    if current_user.is_administrator():
        return redirect(url_for("main.search_data", form_data=form_data))
    articles = get_article_from_db(form_data)
    if articles is None:
        abort(404)
    return render_template("search_result.html", articles=articles)


@main.route('/search_data/<form_data>', methods=["GET", "POST"])
@admin_required
def search_data(form_data):
    if form_data is None:
        abort(404)
    articles = get_article_from_search(form_data)
    if articles is None:
        abort(404)
    for article in articles:
        article = encode_string_dict(article)
        article["body"] = put_linesep_in(article["body"])
    return render_template("downdata_result.html", articles=articles)


def encode_string_dict(string_dict):

    for key in string_dict.keys():
        string_dict[key] = string_dict[key].decode("utf-8").encode("gbk", "ignore")
    return string_dict


def put_linesep_in(string_body):
    put_linesep = re.compile(u"。")
    string_body = put_linesep.sub(u"。<br/>", string_body)
    print "string:%s" % string_body
    return string_body


@main.route('/memento/<prototype_id>')
def memento(prototype_id):
    form = MementoForm()
    prototype_body = Prototype.query.filter_by(id=prototype_id).first().body
    return render_template("memento.html", form=form, prototype=prototype_body)
