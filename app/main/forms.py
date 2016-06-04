#!/usr/bin/env python

from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email


class SignupForm(Form):
    email = StringField("Input your email address", validators=[DataRequired(), Email(), Length(1, 64)])
    name = StringField("Input your name", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField("Input your password", validators=[DataRequired()])
    submit = SubmitField("Signup")
