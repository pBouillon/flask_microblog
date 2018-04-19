from flask import render_template

from app import app


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
