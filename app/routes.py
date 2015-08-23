#-*- coding:utf-8 -*-
from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tkdrmsld123@localhost/howsmart'
app.config['SECRET_KEY'] = 'SET T0 4NY SECRET KEY L1KE RAND0M H4SH'
from models import db
db.init_app(app)

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask import get_flashed_messages
from flask.ext.login import LoginManager, UserMixin, current_user,login_user, logout_user
from forms import SignupForm

@app.route('/')
def main():
    return render_template('main.html')

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
        form = SignupForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('test.html', form=form)
        else:   
            return "[1] Create a new user [2] sign in the user [3] redirect to the user's profile"

    if request.method == 'GET':
        return render_template('test.html', form=form)
