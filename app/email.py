#!/usr/bin/env python
# coding=utf-8

from flask_login import current_app
from flask_mail import Message
from flask import render_template
from threading import Thread
from app import mail


def send_async_email(c_app, msg):
    with c_app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    msg = Message(current_app.config["FLASKY_MAIL_SUBJECT_PREFIX"] + subject,
                  sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[current_app._get_current_object(), msg])
    thr.start()
    return thr
