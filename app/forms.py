from flask.ext.wtf import Form
from wtforms import TextField,TextAreaField, SubmitField, validators, ValidationError, PasswordField, FileField
from models import db, User

class SignupForm(Form):
    username    = TextField('username', [validators.Required('please enter your username')])
    email       = TextField('email', [validators.Required('please enter your email'), validators.Email('please enter your email address')])
    password    = PasswordField('password', [validators.Required('please enter your password')])
    submit      = SubmitField('create account')

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append('That email is aleady taken')
            return False
        else :
            return True

class CompanySignupForm(Form):
    username    = TextField('username', [validators.Required('please enter your company name')])
    email       = TextField('email', [validators.Required('please enter your company email'), validators.Email('please enter your company email')])
    password    = PasswordField('password', [validators.Required('please enter your password')])
    introduction = TextAreaField('introduction', [validators.Required('please enter your company introduction')])
    address     = TextField('address', [validators.Required('please enter your company address')])
    tel         = TextField('tel', [validators.Required('please enter your company tel')])
    website     = TextField('website', [validators.Required('please enter your company website address')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
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

class WriteFeedForm(Form):
    title       = TextField('title', [validators.Required('please enter this feed title')])
    body        = TextAreaField('body', [validators.Required('please enter this feed body')])
    filename    = FileField('filename', [validators.Required('please enter this feed image file')])

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
