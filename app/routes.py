from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for

from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Python is awesome !'
        },
        {
            'author': {'username': 'Simon'},
            'body': 'The cake is a lie.'
        }
    ]
    return render_template('index.html', title='Home page', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # a user already authenticated is redirected to homepage
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    # redirection on the same page if form invalid
    if not form.validate_on_submit():
        return render_template(
            'login.html',
            title='Sign In',
            form=form
        )

    # query the user
    user = User.query.filter_by(
        username=form.username.data
    ).first()

    # if credential doesn't match any user, redirect on login
    if user is None \
            or not user.check_password(form.password.data):
        flash('Invalid username or password')
        return redirect(url_for('login'))

    # load the requested user
    login_user(
        user,
        remember=form.remember_me.data
    )

    # redirect on previous page or on homepage
    next_page = request.args.get('next')

    if not next_page \
            or url_parse(next_page).netloc != '':
        next_page = url_for('index')

    return redirect(next_page)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)
@app.route('/register', methods=['GET', 'POST'])
def register():
    # redirect logged in users to home page
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if not form.validate_on_submit():
        return render_template(
            'register.html',
            title='Register',
            form=form
        )
    user = User(
        username=form.username.data,
        email=form.email.data
    )
    user.set_password(
        form.password.data
    )

    db.session.add(user)
    db.session.commit()

    flash('registered successfully !')

    return redirect(url_for('login'))

