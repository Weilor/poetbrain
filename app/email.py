#!/usr/bin/env python
# coding=utf-8

from flask_login import current_app
from flask_mail import Message
from flask import render_template
from threading import Thread
from app import mail


def send_async_email(c_app, msg):
    """
    多线程发送邮件，这个就是子线程程序。
    :param c_app,current app context
    :param msg,message to be sent
    """
    with c_app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    """
    邮件发送程序
    :param to,destination address
    :param subject,title
    :param template,the text and html template that mail uses
    :param **kwargs,non-use for now
    """
    msg = Message(current_app.config["FLASKY_MAIL_SUBJECT_PREFIX"] + subject,
                  sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[current_app._get_current_object(), msg])
    thr.start()
    return thr
