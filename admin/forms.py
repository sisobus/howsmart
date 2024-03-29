#-*- coding:utf-8 -*-
from flask.ext.wtf import Form,widgets
from wtforms import widgets,TextField,TextAreaField, SubmitField, validators, ValidationError, PasswordField, FileField, RadioField, SelectField, SelectMultipleField
from models import db, User
import utils

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class CompanySearchForm(Form):
    company_si = SelectField('search_company_si', choices=[])
    company_gu = SelectField('search_company_gu', choices=[])
    company_dong = SelectField('search_company_dong', choices=[])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)


class SigninForm(Form):
    email       = TextField('email', [validators.Required('please enter your email')])
    password    = PasswordField('password', [validators.Required('please enter your password')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        '''
        if not Form.validate(self):
            return False
            '''

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user and user.level != 99:
            return False
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append('invalid email or password')
            return False

def get_feed_category_list():
    l = [
        ('1','거실'),
        ('2','주방'),
        ('3','침실'),
        ('4','서재'),
        ('5','유아/주니어방'),
        ('6','욕실'),
        ('7','현관'),
        ('8','기타'),
        ('9','상업공간'),
        ('10','사무공간'),
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

class FindProsForm(Form):
    d = utils.get_address_list()
    company_si  = SelectField('company_si', choices=d['si'])
    company_gu  = SelectField('company_gu', choices=d['gu'])
    company_dong  = SelectField('company_dong', choices=d['dong'])
    company_name = TextField('company_name', [validators.Required('please enter company_name')])
    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return True

