from _md5 import md5
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app import db
from app import login

POST_LEN = 256


@login.user_loader
def load_user(usr_id: str):
    return User.query.get(int(usr_id))


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # user's nickname
    username = db.Column(
        db.String(64),
        index=True,
        unique=True
    )

    # user's email
    email = db.Column(
        db.String(120),
        index=True,
        unique=True
    )

    # hashed user password
    password_hash = db.Column(
        db.String(128)
    )

    posts = db.relationship(
        'Post',
        backref='author',
        lazy='dynamic'
    )

    # user description
    about_me = db.Column(db.String(140))

    # last time the user opened a page
    last_seen = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # many to many relationship
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(
                followers.c.follower_id == id
        ),
        secondaryjoin=(
                followers.c.followed_id == id
        ),
        backref=db.backref(
            'followers',
            lazy='dynamic'
        ),
        lazy='dynamic'
    )

    def avatar(self, size):
        digest = md5(
            self.email
                .lower()
                .encode('utf-8')
        ).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest,
            size
        )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        followed = Post.query.join(
            followers,
            (followers.c.followed_id == Post.user_id)
        ).filter(
            followers.c.follower_id == self.id
        )
        own = Post.query.filter_by(
            user_id=self.id
        )
        return followed.union(own) \
            .order_by(Post.timestamp.desc())

    def is_following(self, user) -> bool:
        return self.followed.filter(
            followers.c.followed_id == user.id
        ).count() > 0

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
