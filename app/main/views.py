#!/usr/bin/env python

from . import main
from flask import render_template


@main.route('/')
def index():
    return render_template("index.html")


@main.route('/user/<username>')
def user_page(username):
    return render_template("user_page.html", name=username)


