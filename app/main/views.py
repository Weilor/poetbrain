#!/usr/bin/env python
# coding=utf-8

from . import main
from app import db
from app.tools import put_linesep_in, get_article_from_search, get_article_from_db, encode_string_dict, check_memento
from forms import ProfileForm, MementoForm
from flask import render_template, abort, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app.models import User, Prototype, Article
from app.decorator import admin_required
import copy


@main.route('/', methods=["GET", "POST"])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Prototype.query.paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                          error_out=False)
    prototypes = copy.deepcopy(pagination.items)
    for prototype in prototypes:
        prototype.body = put_linesep_in(prototype.body)
    return render_template("index.html", prototypes=prototypes, pagination=pagination)


@main.route('/spark')
def spark():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("spark.html", articles=articles)


@main.route('/user/<username>')
def user_page(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    return render_template("user_page.html", user=user, articles=user.articles)


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


@main.route('/search', methods=["GET", "POST"])
def search():
    form_data = request.form.get("content", default=None)
    if form_data is None:
        abort(404)
    if current_user.is_administrator():
        return redirect(url_for("main.search_data", form_data=form_data))
    articles = copy.deepcopy(get_article_from_db(form_data))
    if articles is None:
        abort(404)
    for article in articles:
        article.body = put_linesep_in(article.body)
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


@main.route('/memento/<prototype_id>', methods=["GET", "POST"])
def memento(prototype_id):
    form = MementoForm()
    prototype = Prototype.query.filter_by(id=prototype_id).first()
    if form.validate_on_submit():
        article_text, incorrect_count = check_memento(prototype.body, form.article_text.data)
        article = Article(title=prototype.title,
                          body=article_text,
                          author=current_user._get_current_object(),
                          prototype=prototype,
                          rate=float(incorrect_count/len(prototype.body)))
        db.session.add(article)
        db.session.commit()
        return redirect(url_for("main.user_page", username=current_user.username))
    return render_template("memento.html", form=form, prototype=prototype.title)
