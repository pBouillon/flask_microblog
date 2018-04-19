from datetime import datetime

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
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User


@app.before_request
def before_request():
    """
    updates the 'last seen' field
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.errorhandler(404)
def not_found_error():
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


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


@app.route('/user/<username>')
@login_required
def user(username):
    requested_user = User.query.filter_by(
        username=username
    ).first_or_404()

    posts = [
        {
            'author': requested_user,
            'body': 'test post #1'
        },
        {
            'author': requested_user,
            'body': 'test post #2'
        }
    ]

    return render_template(
        'user.html',
        user=requested_user,
        posts=posts
    )


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash('Your changes have been saved.')

        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template(
        'edit_profile.html',
        title='Edit Profile',
        form=form
    )
