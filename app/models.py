from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(54))
    created_at = db.Column(db.DateTime)
    level = db.Column(db.Integer, default=1)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Feed(db.Model):
    __tablename__ = 'feed'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(120))
    created_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))

    def __init__(self, title, body, created_at):
        self.title = title
        self.body  = body
        self.created_at = created_at


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    created_at = db.Column(db.DateTime)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, body, created_at):
        self.body = body
        self.created_at = created_at

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, image_path):
        self.image_path = image_path


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))


class UserLike(db.Model):
    __tablename__ = 'user_like'
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    company_introduction    = db.Column(db.String(1000))
    company_address         = db.Column(db.String(500))
    company_tel             = db.Column(db.String(100))
    company_website         = db.Column(db.String(500))
    user_id                 = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, company_introduction, company_address, company_tel, company_website, user_id):
        self.company_introduction   = company_introduction
        self.company_address        = company_address
        self.company_tel            = company_tel
        self.company_website        = company_website
        self.user_id                = user_id

class Project(db.Model):
    __tablename__ = 'project'
    id              = db.Column(db.Integer, primary_key=True)
    project_name    = db.Column(db.String(500))
    company_id      = db.Column(db.Integer, db.ForeignKey('company.id'))
    image_id        = db.Column(db.Integer, db.ForeignKey('image.id'))

class Project_has_feed(db.Model):
    __tablename__ = 'project_has_feed'
    project_id  = db.Column(db.Integer, primary_key=True)
    feed_id     = db.Column(db.Integer, primary_key=True)
