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
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

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
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

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

class User_like_feed(db.Model):
    __tablename__ = 'user_like_feed'
    user_id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, user_id, feed_id):
        self.user_id = user_id
        self.feed_id = feed_id

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
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

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
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    project_type_category_id = db.Column(db.Integer)
    project_si = db.Column(db.String(300))
    project_gu = db.Column(db.String(300))
    project_dong = db.Column(db.String(300))
    style_category_id = db.Column(db.Integer)
    project_area = db.Column(db.String(200))
    project_location = db.Column(db.String(500))
    project_estimate_from = db.Column(db.Integer)
    project_estimate_to = db.Column(db.Integer)
    project_buildtime_from = db.Column(db.Integer)
    project_buildtime_to = db.Column(db.Integer)
    project_estimate_hide = db.Column(db.Boolean)
    project_buildtime_hide = db.Column(db.Boolean)

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
    product_sale_price = db.Column(db.Integer)
    product_price = db.Column(db.Integer)
    product_color = db.Column(db.String(200))
    product_desc = db.Column(db.String(5000))
    product_size = db.Column(db.String(200))
    product_model_name = db.Column(db.String(200))
    product_meterial = db.Column(db.String(200))
    shop_category_id = db.Column(db.Integer, db.ForeignKey('shop_category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    style_category_id = db.Column(db.Integer)
    product_brand = db.Column(db.String(500))
    product_soldby = db.Column(db.String(500))

    def __init__(self, product_name, product_price, product_color, product_desc, product_size, product_model_name, product_meterial,  user_id,created_at):
        self.product_name = product_name
        self.product_price = product_price
        self.product_color = product_color
        self.product_desc = product_desc
        self.product_size = product_size
        self.product_model_name = product_model_name
        self.product_meterial = product_meterial
        self.shop_category_id = 1
        self.user_id = user_id
        self.created_at = created_at

class Product_has_image(db.Model):
    __tablename__ = 'product_has_image'
    product_id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, product_id, image_id):
        self.product_id = product_id
        self.image_id = image_id

class Follow(db.Model):
    __tablename__ = 'follow'
    from_user_id = db.Column(db.Integer, primary_key=True)
    to_user_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, from_user_id, to_user_id):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id

class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(500))

    def __init__(self,id,status_name):
        self.id = id
        self.status_name = status_name

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    tag_x = db.Column(db.Float)
    tag_y = db.Column(db.Float)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    tag_name = db.Column(db.String(300))
    tag_link = db.Column(db.String(300))
    image_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, tag_x, tag_y, feed_id, tag_name, tag_link):
        self.tag_x = tag_x
        self.tag_y = tag_y
        self.feed_id = feed_id
        self.tag_name = tag_name
        self.tag_link = tag_link

class Project_type_category(db.Model):
    __tablename__ = 'project_type_category'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(300))

    def __init__(self, id, type_name):
        self.id = id
        self.type_name = type_name

class Style_category(db.Model):
    __tablename__ = 'style_category'
    id = db.Column(db.Integer, primary_key=True)
    style_name = db.Column(db.String(300))

    def __init__(self, id, style_name):
        self.id = id
        self.style_name = style_name

class Project_hash_tag(db.Model):
    __tablename__ = 'project_hash_tag'
    id = db.Column(db.Integer, primary_key=True)
    hash_tag_name = db.Column(db.String(300))
    project_id  = db.Column(db.Integer, primary_key=True)

    def __init__(self, hash_tag_name, project_id):
        self.hash_tag_name = hash_tag_name
        self.project_id = project_id

class Product_hash_tag(db.Model):
    __tablename__ = 'product_hash_tag'
    id = db.Column(db.Integer, primary_key=True)
    product_hash_tag_name = db.Column(db.String(300))
    product_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, product_hash_tag_name, product_id):
        self.product_hash_tag_name = product_hash_tag_name
        self.product_id = product_id

class Blog_post(db.Model):
    __tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    post_name = db.Column(db.String(500))
    post_body = db.Column(db.String(10000))
    post_summary = db.Column(db.String(500))
    created_at = db.Column(db.DateTime)
    image_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, post_name, post_body, post_summary, created_at,image_id,user_id):
        self.post_name = post_name
        self.post_body = post_body
        self.post_summary = post_summary
        self.created_at = created_at
        self.image_id = image_id
        self.user_id = user_id

class Blog_post_comment(db.Model):
    __tablename__ = 'blog_post_comment'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.String(500))
    created_at = db.Column(db.DateTime)
    blog_post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    status_id = db.Column(db.Integer)

    def __init__(self, body, created_at, blog_post_id, user_id, status_id):
        self.body = body
        self.created_at = created_at
        self.blog_post_id = blog_post_id
        self.user_id = user_id
        self.status_id = status_id

class User_save_feed(db.Model):
    __tablename__ = 'user_save_feed'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(500))

    def __init__(self, user_id, feed_id, comment):
        self.user_id = user_id
        self.feed_id = feed_id
        self.comment = comment

class User_save_post(db.Model):
    __tablename__ = 'user_save_post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(500))

    def __init__(self, user_id, post_id, comment):
        self.user_id = user_id
        self.post_id = post_id
        self.comment = comment

class User_save_product(db.Model):
    __tablename__ = 'user_save_product'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(500))

    def __init__(self, user_id, product_id, comment):
        self.user_id = user_id
        self.product_id = product_id
        self.comment = comment

class User_profile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)

    def __init__(self, user_id, image_id, created_at):
        self.user_id = user_id
        self.image_id = image_id
        self.created_at = created_at

class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    star = db.Column(db.Integer)
    comment = db.Column(db.String(500))
    user_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)

    def __init__(self, star, comment, user_id, company_id, created_at):
        self.star = star
        self.comment = comment
        self.user_id = user_id
        self.company_id = company_id
        self.created_at = created_at

class Qna_q(db.Model):
    __tablename__ = 'qna_q'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)

    def __init__(self, body, user_id, company_id, created_at):
        self.body = body
        self.user_id = user_id
        self.company_id = company_id
        self.created_at = created_at

class Qna_a(db.Model):
    __tablename__ = 'qna_a'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1000))
    qna_q_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, body,qna_q_id, created_at, user_id):
        self.body = body
        self.qna_q_id = qna_q_id
        self.created_at = created_at
        self.user_id = user_id

class Product_has_shop_category(db.Model):
    __tablename__ = 'product_has_shop_category'
    product_id = db.Column(db.Integer, primary_key=True)
    shop_category_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, product_id, shop_category_id):
        self.product_id = product_id
        self.shop_category_id = shop_category_id
