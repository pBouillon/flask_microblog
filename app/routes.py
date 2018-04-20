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
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.forms import EditProfileForm
from app.forms import PostForm
from app.models import User, Post


@app.before_request
def before_request():
    """
    updates the 'last seen' field
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# noinspection PyUnusedLocal
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


# noinspection PyUnusedLocal
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            body=form.post.data,
            author=current_user
        )

        db.session.add(post)
        db.session.commit()

        flash('Your post is now live!')

        return redirect(url_for('index'))

    posts = current_user.followed_posts().all()

    return render_template(
        'index.html',
        title='Home page',
        form=form,
        posts=posts
    )


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
    usr = User.query.filter_by(
        username=form.username.data
    ).first()

    # if credential doesn't match any user, redirect on login
    if usr is None \
            or not usr.check_password(form.password.data):
        flash('Invalid username or password')
        return redirect(url_for('login'))

    # load the requested user
    login_user(
        usr,
        remember=form.remember_me.data
    )

    # redirect on previous page or on homepage
    page = request.args.get(
        'page',
        1,
        type=int
    )

    posts = current_user.followed_posts().paginate(
        page,
        app.config['POSTS_PER_PAGE'],
        False
    )

    next_url = url_for(
        'index',
        page=posts.next_num
    ) if posts.has_next else None

    prev_url = url_for(
        'index',
        page=posts.prev_num
    ) if posts.has_prev else None

    return render_template(
        'index.html',
        title='Home',
        form=form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# noinspection PyArgumentList
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
    usr = User(
        username=form.username.data,
        email=form.email.data
    )
    usr.set_password(
        form.password.data
    )

    db.session.add(usr)
    db.session.commit()

    flash('registered successfully !')

    return redirect(url_for('login'))


@app.route('/user/<username>')
@login_required
def user(username):
    usr = User.query.filter_by(
        username=username
    ).first_or_404()

    page = request.args.get(
        'page',
        1,
        type=int
    )

    posts = usr.posts.order_by(
        Post.timestamp.desc()
    ).paginate(
        page,
        app.config['POSTS_PER_PAGE'],
        False
    )

    next_url = url_for(
        'user',
        username=usr.username,
        page=posts.next_num
    ) if posts.has_next else None

    prev_url = url_for(
        'user',
        username=usr.username,
        page=posts.prev_num
    ) if posts.has_prev else None

    return render_template(
        'user.html',
        user=usr,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
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


@app.route('/follow/<username>')
@login_required
def follow(username: str):
    usr = User.query.filter_by(
        username=username
    ).first()

    if usr is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))

    if usr == current_user:
        flash('You cannot follow yourself !')
        return redirect(url_for('index'))

    current_user.follow(usr)
    db.session.commit()

    flash('You are following {}!'.format(username))

    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    usr = User.query.filter_by(
        username=username
    ).first()

    if usr is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))

    if usr == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for(
            'user',
            username=username
        ))

    current_user.unfollow(usr)
    db.session.commit()

    flash('You are not following {}.'.format(username))

    return redirect(url_for('user', username=username))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get(
        'page',
        1,
        type=int
    )

    posts = Post.query.order_by(
        Post.timestamp.desc()
    ).paginate(
        page,
        app.config['POSTS_PER_PAGE'],
        False
    )

    next_url = url_for(
        'explore',
        page=posts.next_num
    ) if posts.has_next else None

    prev_url = url_for(
        'explore',
        page=posts.prev_num
    ) if posts.has_prev else None

    return render_template(
        "index.html",
        title='Explore',
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )
