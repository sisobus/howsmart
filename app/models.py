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
    title = db.Column(db.String(1000))
    body = db.Column(db.String(5000))
    created_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    feed_category_id = db.Column(db.Integer, db.ForeignKey('feed_category.id'))

    def __init__(self, title, body, created_at):
        self.title = title
        self.body  = body
        self.created_at = created_at

class Feed_category(db.Model):
    __tablename__ = 'feed_category'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(500))


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(2000))
    created_at = db.Column(db.DateTime)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, body, created_at):
        self.body = body
        self.created_at = created_at

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime)

    def __init__(self, image_path):
        self.image_path = image_path


class UserLike(db.Model):
    __tablename__ = 'user_like'
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    company_introduction    = db.Column(db.String(5000))
    company_address         = db.Column(db.String(500))
    company_tel             = db.Column(db.String(100))
    company_website         = db.Column(db.String(500))
    user_id                 = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id                = db.Column(db.Integer, db.ForeignKey('image.id'))
    company_si              = db.Column(db.String(500))
    company_gu              = db.Column(db.String(500))
    company_dong            = db.Column(db.String(500))

    def __init__(self, company_introduction, company_address, company_tel, company_website, user_id,company_si,company_gu,company_dong):
        self.company_introduction   = company_introduction
        self.company_address        = company_address
        self.company_tel            = company_tel
        self.company_website        = company_website
        self.user_id                = user_id
        self.company_si             = company_si
        self.company_gu             = company_gu
        self.company_dong           = company_dong

class Project(db.Model):
    __tablename__ = 'project'
    id              = db.Column(db.Integer, primary_key=True)
    project_name    = db.Column(db.String(1500))
    company_id      = db.Column(db.Integer, db.ForeignKey('company.id'))
    image_id        = db.Column(db.Integer, db.ForeignKey('image.id'))
    created_at = db.Column(db.DateTime)
    project_body    = db.Column(db.String(5000))
    project_credit  = db.Column(db.String(500))

    def __init__(self, project_name, company_id, image_id, created_at, project_body, project_credit):
        self.project_name = project_name
        self.company_id = company_id
        self.image_id = image_id
        self.created_at = created_at
        self.project_body = project_body
        self.project_credit = project_credit

class Project_has_feed(db.Model):
    __tablename__ = 'project_has_feed'
    project_id  = db.Column(db.Integer, primary_key=True)
    feed_id     = db.Column(db.Integer, primary_key=True)

    def __init__(self, project_id, feed_id):
        self.project_id = project_id
        self.feed_id = feed_id

class Pros_category(db.Model):
    __tablename__ = 'pros_category'
    id = db.Column(db.Integer, primary_key=True)
    category_name   = db.Column(db.String(500))

    def __init__(self, category_name):
        self.category_name = category_name

class Company_has_pros_category(db.Model):
    __tablename__ = 'company_has_pros_category'
    company_id = db.Column(db.Integer, primary_key=True)
    pros_category_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, company_id, pros_category_id):
        self.company_id = company_id
        self.pros_category_id = pros_category_id

class Shop_category(db.Model):
    __tablename__ = 'shop_category'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(200))

    def __init__(self,category_name):
        self.category_name = category_name

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(1000))
    product_price = db.Column(db.Integer)
    product_color = db.Column(db.String(200))
    product_desc = db.Column(db.String(5000))
    product_size = db.Column(db.String(200))
    product_model_name = db.Column(db.String(200))
    product_meterial = db.Column(db.String(200))
    shop_category_id = db.Column(db.Integer, db.ForeignKey('shop_category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime)

    def __init__(self, product_name, product_price, product_color, product_desc, product_size, product_model_name, product_meterial, shop_category_id, user_id,created_at):
        self.product_name = product_name
        self.product_price = product_price
        self.product_color = product_color
        self.product_desc = product_desc
        self.product_size = product_size
        self.product_model_name = product_model_name
        self.product_meterial = product_meterial
        self.shop_category_id = shop_category_id
        self.user_id = user_id
        self.created_at = created_at

class Product_has_image(db.Model):
    __tablename__ = 'product_has_image'
    product_id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, product_id, image_id):
        self.product_id = product_id
        self.image_id = image_id
