from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SiteConfig(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(256))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    order = db.Column(db.Integer, default=0)
    links = db.relationship('Link', backref='category', lazy='dynamic', cascade="all, delete-orphan")

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(256))
    icon = db.Column(db.String(64), default='fa-globe')  # FontAwesome icon class
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    clicks = db.Column(db.Integer, default=0)
