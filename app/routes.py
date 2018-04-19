from flask import render_template, flash, redirect

from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {
        'username': 'pBouillon'
    }
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
    return render_template('index.html', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if not form.validate_on_submit():
        return render_template(
            'login.html',
            title='Sign In',
            form=form
        )

    flash(
        'Login requested for user {}, remember_me={}'.format(
            form.username.data,
            form.remember_me.data
        )
    )
    return redirect('/index')
