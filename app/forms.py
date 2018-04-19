from flask_wtf import FlaskForm

from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import SubmitField

from wtforms.validators import DataRequired, ValidationError
from wtforms.validators import EqualTo
from wtforms.validators import Email

from app.models import User


PASSWORD_MIN_LEN = 8


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    password2 = PasswordField(
        'Repeat Password',
        validators=[
            DataRequired(),
            EqualTo('password')
        ]
    )
    submit = SubmitField('Register')

    def validate_username(self, username) -> None:
        user = User.query.filter_by(
            username=username.data
        ).first()

        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email) -> None:
        # TODO implements check -> https://haveibeenpwned.com
        user = User.query.filter_by(
            email=email.data
        ).first()

        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_password(self, password) -> None:
        # TODO implements check -> https://haveibeenpwned.com
        password_value = password.data

        if len(password_value) < PASSWORD_MIN_LEN:
            raise ValidationError('Password must be at least 8 characters')
