from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config


# flask instance
app = Flask(__name__)
app.config.from_object(Config)

# login
login = LoginManager(app)
login.login_view = 'login'

# database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import models
from app import routes

