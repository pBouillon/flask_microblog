from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import SubmitField

from wtforms.validators import DataRequired
# noinspection PyProtectedMember
from wtforms.validators import ValidationError
from wtforms.validators import Length
from wtforms.validators import EqualTo
from wtforms.validators import Email

from app.models import User


PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 64


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
        validators=[
            DataRequired(),
            Email()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=PASSWORD_MIN_LEN, max=PASSWORD_MAX_LEN)
        ]
    )
    password2 = PasswordField(
        'Repeat Password',
        validators=[
            DataRequired(),
            EqualTo('password')
        ]
    )
    submit = SubmitField('Register')

    # noinspection PyMethodMayBeStatic
    def validate_username(self, username) -> None:
        user = User.query.filter_by(
            username=username.data
        ).first()

        if user is not None:
            raise ValidationError('Please use a different username.')

    # noinspection PyMethodMayBeStatic
    def validate_email(self, email) -> None:
        # TODO implements check -> https://haveibeenpwned.com
        user = User.query.filter_by(
            email=email.data
        ).first()

        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_password(self, password) -> None:
        # TODO implements check -> https://haveibeenpwned.com
        # password_value = password.dataeast 8 characters')
        pass


class EditProfileForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    about_me = TextAreaField(
        'About me',
        validators=[Length(min=0, max=140)]
    )
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """
        prevent username duplication
        """
        if username.data != self.original_username:
            user = User.query.filter_by(
                username=self.username.data
            ).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
