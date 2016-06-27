#-*- coding:utf-8 -*-
from flask.ext.wtf import Form,widgets
from wtforms import widgets,TextField,TextAreaField, SubmitField, validators, ValidationError, PasswordField, FileField, RadioField, SelectField, SelectMultipleField, IntegerField, BooleanField
from models import db, User, Project_type_category,Style_category
import utils
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask

class SignupForm(Form):
    username    = TextField('username', [validators.Required(u'이름을 작성해주세요')])
    email       = TextField('email', [validators.Required(u'이메일을 작성해주세요.'), validators.Email(u'이메일 주소를 정확히 입력해주세요.')])
    password    = PasswordField('password', [validators.Required(u'비밀번호를 작성해주세요')])
    password_check = PasswordField('password_check', [validators.Required('비밀번호를 한번 더 입력해주세요')])
    submit      = SubmitField('create account')

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        if self.password.data != self.password_check.data:
            self.password_check.errors.append(u'패스워드가 다릅니다.')
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append(u'이메일이 이미 존재합니다.')
            return False
        else :
            return True

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class CompanySearchForm(Form):
    company_si = SelectField('search_company_si', choices=[])
    company_gu = SelectField('search_company_gu', choices=[])
    company_dong = SelectField('search_company_dong', choices=[])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)



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
    pros_category = MultiCheckboxField('pros_category', choices=[('1','주거 인테리어'),('2','상업 인테리어'),('4','홈스타일링'),('3','가구(제작가구)'),('6','인테리어 디자이너')])
#     shop_category = SelectField('shop_category', choices=utils.get_shop_category_list())

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        if self.password.data != self.password_check.data:
            self.password_check.errors.append('password(%s), password_check(%s) is not same'%(self.password.data,self.password_check.data))
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append('That email is aleady taken')
            return False
        else :
            return True

class SigninForm(Form):
    email       = TextField('email', [validators.Required(u'가입하신 이메일을 입력해주세요')])
    password    = PasswordField('password', [validators.Required(u'비밀번호를 입력해주세요')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append(u'비밀번호가 틀렸습니다')
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

def get_project_type_category_list():
    l = [
            ('1',u'없음'),
            ('2',u'원룸'),
            ('3',u'투룸'),
            ('4',u'오피스텔'),
            ('5',u'아파트'),
            ('6',u'빌라연립'),
            ('7',u'단독주택'),
            ('8',u'사무공간'),
            ('9',u'상업공간'),
            ('10',u'기타'),
            ]
    return l

def get_style_category_list():
    l = []
    l = [
            ('1',u'없음'),
            ('2',u'모던'),
            ('3',u'북유럽'),
            ('4',u'빈티지'),
            ('5',u'내츄럴'),
            ('6',u'프로방스'),
            ('7',u'클래식+앤틱'),
            ('8',u'오리엔탈'),
            ('9',u'유니크'),
            ('10',u'기타'),
            ]
    return l

class CreateProjectForm(Form):
    project_name    = TextField('project_name', [validators.Required('please enter project name')])
    project_body    = TextAreaField('body', [validators.Required('please enter this project body')])
    project_credit  = TextField('project_credit', [validators.Required('please enter project credit')])
    project_type_category = SelectField('project_type_category',choices=get_project_type_category_list(),validators=[validators.Required('please enter type')])
    d = utils.get_address_list()
    project_si = SelectField('company_si', choices=d['si'], validators=[validators.Required('si')])
    project_gu  = SelectField('company_gu', choices=d['gu'], validators=[validators.Required('gu')])
    project_dong  = SelectField('company_dong', choices=d['dong'], validators=[validators.Required('dong')])
    project_style_category = SelectField('project_style_category',choices=get_style_category_list(), validators=[validators.Required('style')])
    project_area = SelectField('project_area',choices=[('1',u'10평대미만'),('2',u'10평대'),('3',u'20평대'),('4',u'30평대'),('5',u'40평대'),('6',u'50평대이상')],validators=[validators.Required('area')])
    project_location = TextField('project_location',validators=[validators.Optional()])
    hash_tag = TextField('hash_tag',validators=[validators.Optional()])
    project_estimate_from = IntegerField('project_estimate_from', validators=[validators.Optional()])
    project_estimate_to = IntegerField('project_estimate_to', validators=[validators.Optional()])
    project_estimate_hide = BooleanField('project_estimate_hide', validators=[validators.Optional()])
    project_buildtime_from = IntegerField('project_buildtime_from', validators=[validators.Optional()])
    project_buildtime_to = IntegerField('project_buildtime_to', validators=[validators.Optional()])
    project_buildtime_hide = BooleanField('project_buildtime_hide', validators=[validators.Optional()])


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
#    shop_category = SelectField('shop_category', choices=utils.get_shop_category_list())
    shop_category = MultiCheckboxField('shop_category', choices=utils.get_shop_category_list())
    product_style_category = SelectField('product_style_category',choices=get_style_category_list(), validators=[validators.Optional()])
    hash_tag = TextField('hash_tag',validators=[validators.Optional()])
    product_brand = TextField('product_brand', [validators.Required('brand')])
    product_soldby = TextField('product_soldby', [validators.Required('soldby')])

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

class AddTagForm(Form):
    tag_name = TextField('tag_name',[validators.Required('tag_name')])
    tag_link = TextField('tag_link',[validators.Required('tag_link')])
    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)
    def validate(self):
        if not Form.validate(self):
            return False
        return True

class ReviewCommentForm(Form):
    comment =  TextAreaField('comment', [validators.Required('please enter your comment')])
    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)
    def validate(self):
        if not Form.validate(self):
            return False
        return True

class QnaQForm(Form):
    body = TextAreaField('body',[validators.Required('question body')])
    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)
    def validate(self):
        if not Form.validate(self):
            return False
        return True

class QnaAForm(Form):
    body = TextField('body',[validators.Required('answer body')])
    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)
    def validate(self):
        if not Form.validate(self):
            return False
        return True

class FindPasswordForm(Form):
    email = TextField('email',[validators.Required('email')])
    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)
    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(email=self.email.data.lower()).first()
        if not user:
            self.email.errors.append(u'이메일이 존재하지 않습니다.')
            return False
        return True

class ChangePasswordForm(Form):
    cur_password    = PasswordField('cur_password', [validators.Required(u'비밀번호를 작성해주세요')])
    next_password    = PasswordField('next_password', [validators.Required(u'비밀번호를 작성해주세요')])
    next_password_check = PasswordField('next_password_check', [validators.Required('비밀번호를 한번 더 입력해주세요')])
    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)
    def validate(self):
        if not Form.validate(self):
            return False
        return True
