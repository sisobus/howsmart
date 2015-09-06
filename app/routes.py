# -*- coding:utf-8 -*-
from flask import Flask, url_for
from werkzeug import secure_filename
import utils
import os

from config import UPLOAD_FOLDER, HOWSMART_DATABASE_URI, HOWSMART_SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']   = HOWSMART_DATABASE_URI
app.config['SECRET_KEY']                = HOWSMART_SECRET_KEY
app.config['UPLOAD_FOLDER']             = UPLOAD_FOLDER

from models import db, User, Feed, Image, Comment

db.init_app(app)

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask import get_flashed_messages
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
from forms import SignupForm, SigninForm, WriteFeedForm, CommentForm
from datetime import datetime


@app.route('/')
def main():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()

    feeds = Feed.query.order_by(Feed.created_at.desc()).limit(10).all()
    ret_feeds = []
    for feed in feeds:
        d = {}
        image = Image.query.filter_by(id=feed.image_id).first()
        image_path = utils.get_image_path(image.image_path)
        user = User.query.filter_by(id=feed.user_id).first()
        all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()
        d['image_path'] = image_path
        d['user'] = user
        d['feed'] = feed
        d['number_of_comment'] = len(all_comments)
        ret_feeds.append(d)

    return render_template('main.html', signupForm=signupForm, signinForm=signinForm, feeds=ret_feeds)



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
            newuser.created_at = datetime.utcnow()
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

@app.route('/write_feed',methods=['GET','POST'])
def write_feed():
    with app.app_context():
        writeFeedForm = WriteFeedForm()

    if request.method == 'POST':
        if not writeFeedForm.validate():
            return render_template('write_feed.html', writeFeedForm=writeFeedForm)
        else :
            user = User.query.filter_by(email=session['email'].lower()).first()
            if writeFeedForm.validate_on_submit():
                filename = secure_filename(writeFeedForm.filename.data.filename)
                if utils.allowedFile(filename):
                    directory_url = os.path.join(app.config['UPLOAD_FOLDER'],session['email'])
                    utils.createDirectory(directory_url)
                    file_path = os.path.join(directory_url,filename)
                    writeFeedForm.filename.data.save(file_path)
                    image = Image(file_path)
                    image.user_id = user.id
                    db.session.add(image)
                    db.session.commit()
                feed = Feed(writeFeedForm.title.data, writeFeedForm.body.data, datetime.utcnow())
                feed.user_id = user.id
                feed.image_id = image.id
                db.session.add(feed)
                db.session.commit()
            return redirect(url_for('main'))
    elif request.method == 'GET':
        return render_template('write_feed.html',writeFeedForm=writeFeedForm)

@app.route('/feed_detail/<int:feed_id>',methods=['GET','POST'])
def feed_detail(feed_id):
    with app.app_context():
        commentForm = CommentForm()

    feed = Feed.query.filter_by(id=feed_id).first()
    image = Image.query.filter_by(id=feed.image_id).first()
    user = User.query.filter_by(id=feed.user_id).first()
    image_path = utils.get_image_path(image.image_path)

    all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()
    ret = {}
    ret['feed'] = feed
    ret['user'] = user
    ret['image_path'] = image_path

    if request.method == 'GET':
        return render_template('feed_detail.html',ret=ret,commentForm=commentForm,all_comments=all_comments)
    elif request.method == 'POST':
        if not commentForm.validate():
            return render_template('feed_detail.html',ret=ret,commentForm=commentForm,all_comments=all_comments)

        if commentForm.validate_on_submit():
            comment = Comment(commentForm.body.data, datetime.utcnow())
            comment_user = User.query.filter_by(email=session['email'].lower()).first()
            comment.user_id = comment_user.id
            comment.feed_id = feed.id
            db.session.add(comment)
            db.session.commit()
            all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()
        return redirect(url_for('feed_detail', feed_id=feed.id))

@app.route('/upload_file',methods=['GET','POST'])
def uploadFile():
    if request.method == 'POST':
        file = request.files['file']
        if file and utils.allowedFile(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            return redirect(url_for('uploadedFile',filename=filename))
    else:
        return '''
            <!doctype html>
            <h1>Upload new file</h1>
            <form action="upload_file" method=post enctype=multipart/form-data>
            <p><input type=file name=file>
            <input type=submit value=Upload>
            </form>
            </html>
            '''

@app.route('/uploaded_file')
def uploadedFile():
    return '''
        <!doctype html>
        <h1>file is uploaded</h1>
        </html>
    '''
