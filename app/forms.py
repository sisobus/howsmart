#-*- coding:utf-8 -*-
from flask.ext.wtf import Form,widgets
from wtforms import widgets,TextField,TextAreaField, SubmitField, validators, ValidationError, PasswordField, FileField, RadioField, SelectField, SelectMultipleField
from models import db, User
import utils

class SignupForm(Form):
    username    = TextField('username', [validators.Required('please enter your username')])
    email       = TextField('email', [validators.Required('please enter your email'), validators.Email('please enter your email address')])
    password    = PasswordField('password', [validators.Required('please enter your password')])
    password_check = PasswordField('password_check', [validators.Required('please enter your password more')])
    submit      = SubmitField('create account')

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        if self.password != self.password_check:
            self.password_check.errors.append('password is not same')
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append('That email is aleady taken')
            return False
        else :
            return True

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class CompanySignupForm(Form):
    username    = TextField('username', [validators.Required('please enter your company name')])
    email       = TextField('email', [validators.Required('please enter your company email'), validators.Email('please enter your company email')])
    password    = PasswordField('password', [validators.Required('please enter your password')])
    password_check = PasswordField('password_check', [validators.Required('please enter your password more')])
    introduction = TextAreaField('introduction', [validators.Required('please enter your company introduction')])
    address     = TextField('address', [validators.Required('please enter your company address')])
    tel         = TextField('tel', [validators.Required('please enter your company tel')])
    website     = TextField('website', [validators.Required('please enter your company website address')])
    filename    = FileField('filename', [validators.Required('please enter this feed image file')])
    #pros_category = RadioField('pros_category', choices=[('value_1','option1'),('value_2','option2'),('value_3','option3')])
    pros_category = MultiCheckboxField('pros_category', choices=[('1','주거 인테리어'),('2','상업 인테리어'),('4','인테리어 디자이너'),('3','가구 회사')])
    company_si  = SelectField('company_si', choices=[('전체','전체')])
    company_gu  = SelectField('company_gu', choices=[('전체','전체')])
    company_dong  = SelectField('company_dong', choices=[('전체','전체')])
#     shop_category = SelectField('shop_category', choices=utils.get_shop_category_list())

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        if self.password != self.password_check:
            self.password_check.errors.append('password is not same')
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append('That email is aleady taken')
            return False
        else :
            return True

class SigninForm(Form):
    email       = TextField('email', [validators.Required('please enter your email')])
    password    = PasswordField('password', [validators.Required('please enter your password')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append('invalid email or password')
            return False

def get_feed_category_list():
    l = [
        ('1','주방'),
        ('2','화장실'),
        ('3','방'),
        ('4','거실'),
        ('5','현관'),
        ('6','주거공간_기타'),
        ('7','카페'),
        ('8','식당'),
        ('9','사무실'),
        ('10','상업공간_기타'),
    ]
    return l

class WriteFeedForm(Form):
    title       = TextField('title', [validators.Required('please enter this feed title')])
    body        = TextAreaField('body', [validators.Required('please enter this feed body')])
    filename    = FileField('filename', [validators.Required('please enter this feed image file')])
    feed_category = RadioField('feed_category', choices=get_feed_category_list())
    #feed_category = RadioField('feed_category', choices=[('1','option1'),('2','option2'),('value_3','option3')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return True


class ProjectEditForm(Form):
    title       = TextField('title', [validators.Required('please enter this feed title')])
    body        = TextAreaField('body', [validators.Required('please enter this feed body')])
    feed_category = RadioField('feed_category', choices=get_feed_category_list())
    #feed_category = RadioField('feed_category', choices=[('1','option1'),('2','option2'),('value_3','option3')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return True

class CreateProjectForm(Form):
    project_name    = TextField('project_name', [validators.Required('please enter project name')])
    project_body    = TextAreaField('body', [validators.Required('please enter this project body')])
    project_credit  = TextField('project_credit', [validators.Required('please enter project credit')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return True

class MakeProjectForm(Form):
    project_name    = TextField('project_name', [validators.Required('please enter project name')])
    title       = TextField('title', [validators.Required('please enter this feed title')])
    body        = TextAreaField('body', [validators.Required('please enter this feed body')])
    filename    = FileField('filename', [validators.Required('please enter this feed image file')])
    feed_category = RadioField('feed_category', choices=get_feed_category_list())
    project_body    = TextAreaField('body', [validators.Required('please enter this project body')])
    project_credit  = TextField('project_credit', [validators.Required('please enter project credit')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return True

class CommentForm(Form):
    body        = TextField('body', [validators.Required('please enter your comment')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return True


class CreateProductForm(Form):
    product_name = TextField('product_name', [validators.Required('please enter product Name')])
    product_price = TextField('product_price', [validators.Required('please enter product price')])
    product_color = TextField('product_color', [validators.Required('please enter product color')])
    product_desc = TextAreaField('product_desc', [validators.Required('please enter product description')])
    product_size = TextField('product_size', [validators.Required('please enter product size')])
    product_model_name = TextField('product_model_name', [validators.Required('please enter product model name')])
    product_meterial = TextField('product_meterial', [validators.Required('please enter product meterial')])
    shop_category = SelectField('shop_category', choices=utils.get_shop_category_list())

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return True
