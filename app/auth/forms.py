from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from app.models import User


class LoginForm(Form):
    user_name = StringField("Username", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField("Please input your password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log in")


class SignupForm(Form):
    email = StringField("Input your email address", validators=[DataRequired(), Email(), Length(1, 64)])
    name = StringField("Input your name", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField("Input your password", validators=[DataRequired()])
    submit = SubmitField("Signup")

    @staticmethod
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    @staticmethod
    def validate_name(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')