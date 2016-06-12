#!/usr/bin/env python
# coding=utf-8

from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, RadioField
from wtforms.validators import Length


class ProfileForm(Form):
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField("Submit")


class MementoForm(Form):
    article_text = TextAreaField("It's time to show your memento")
    submit = SubmitField("Submit")


class UpdateDataForm(Form):
    dynasty_or_author = RadioField("Choose",choices=[('dynasty', 'dynasty'), ('author', 'author')])
    d_or_a_text = StringField("Input")
    submit = SubmitField("Submit")
