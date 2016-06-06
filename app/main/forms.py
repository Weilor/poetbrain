#!/usr/bin/env python
# coding=utf-8

from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Length


class ProfileForm(Form):
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField("Submit")
