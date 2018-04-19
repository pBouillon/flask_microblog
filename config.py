from os import environ
from os import path


basedir = path.abspath(
    path.dirname(__file__)
)


class Config:
    SECRET_KEY = environ.get('SECRET_KEY') or 'super-secret_key'

    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + path.join(
            basedir,
            'app.db)'
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
