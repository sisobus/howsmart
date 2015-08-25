# -*- coding:utf-8 -*-
from flask import Flask, url_for

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tkdrmsld123@1.234.80.248/howsmart'
app.config['SECRET_KEY'] = 'SET T0 4NY SECRET KEY L1KE RAND0M H4SH'
from models import db, User

db.init_app(app)

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask import get_flashed_messages
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
from forms import SignupForm, SigninForm


@app.route('/')
def main():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()

    return render_template('main.html', signupForm=signupForm, signinForm=signinForm)


@app.route('/test')
def test():
    if db.session.query("1").from_statement("SELECT 1").all():
        return 'It works.'
    else:
        return 'Something is broken.'


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    with app.app_context():
        #    with app.test_request_context():
        signupForm = SignupForm()
        signinForm = SigninForm()

    if request.method == 'POST':
        if not signupForm.validate():
            return render_template('main.html', signupForm=signupForm, signinForm=signinForm)
        else:
            newuser = User(signupForm.username.data, signupForm.email.data, signupForm.password.data)
            db.session.add(newuser)
            db.session.commit()

            session['username'] = newuser.username
            session['email'] = newuser.email
            session['logged_in'] = True

            return redirect(url_for('main'))


    if request.method == 'GET':
        return render_template('main.html', signupForm=signupForm, signinForm=signinForm)

@app.route('/signin',methods=['GET','POST'])
def signin():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()

    if request.method == 'POST':
        if not signinForm.validate():
            return render_template('main.html', signupForm=signupForm, signinForm=signinForm)
        else :
            user = User.query.filter_by(email=signinForm.email.data.lower()).first()
            session['email'] = signinForm.email.data
            session['username'] = user.username
            session['logged_in'] = True
            return redirect(url_for('main'))
    elif request.method == 'GET':
        return render_template('main.html', signupForm=signupForm, signinForm=signinForm)


@app.route('/signout')
def signout():
    if 'logged_in' not in session:
        return redirect(url_for('main'))
    session.pop('email', None)
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for('main'))
