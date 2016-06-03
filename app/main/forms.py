#!/usr/bin/env python

from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class SignupForm(Form):
    name = StringField("Input your name", validators=[DataRequired()])
    password = PasswordField("Input your password", validators=[DataRequired()])
    submit = SubmitField("Signup")
