from flask.ext.wtf import Form
from wtforms import TextField,TextAreaField, SubmitField, validators, ValidationError, PasswordField
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

