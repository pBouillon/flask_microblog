from os import environ
from os import path


basedir = path.abspath(
    path.dirname(__file__)
)


class Config:
    #
    # login
    SECRET_KEY = environ.get('SECRET_KEY') or 'super-secret_key'

    #
    # database
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + path.join(
            basedir,
            'app.db)'
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #
    # errors
    MAIL_SERVER = environ.get('MAIL_SERVER')

    MAIL_PORT = int(
        environ.get('MAIL_PORT')
        or 25
    )

    MAIL_USE_TLS = environ.get('MAIL_USE_TLS') is not None

    MAIL_USERNAME = environ.get('MAIL_USERNAME')

    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')

    ADMINS = [
        'your-email@example.com',
    ]

    #
    # pagination
    POSTS_PER_PAGE = 3
