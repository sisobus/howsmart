# -*- coding:utf-8 -*-
from flask import Flask, url_for
from werkzeug import secure_filename
import utils
import os
import time

from config import UPLOAD_FOLDER, HOWSMART_DATABASE_URI, HOWSMART_SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']   = HOWSMART_DATABASE_URI
app.config['SECRET_KEY']                = HOWSMART_SECRET_KEY
app.config['UPLOAD_FOLDER']             = UPLOAD_FOLDER

from models import db, User, Feed, Image, Comment, Company, Project, Project_has_feed, Pros_category, Company_has_pros_category

db.init_app(app)

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask import get_flashed_messages
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
from forms import SignupForm, SigninForm, WriteFeedForm, CommentForm, CompanySignupForm, MakeProjectForm, CreateProjectForm, ProjectEditForm
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


@app.route('/',methods=['GET','POST'])
def main():
    session['project_id'] = 0

    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()


    if request.method == 'GET':
        offset = 10
        feeds = Feed.query.order_by(Feed.created_at.desc()).limit(offset).all()
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

        return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm, feeds=ret_feeds, offset=offset)
    elif request.method == 'POST':
        offset = int(request.form['offset'])
        feeds = Feed.query.order_by(Feed.created_at.desc()).limit(offset).all()
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

        html_code = render_template('main.html', signupForm=signupForm, signinForm=signinForm,companySignupForm=companySignupForm ,feeds=ret_feeds, offset=offset)
        return html_code
#        soup = BeautifulSoup(html_code,"html.parser")
#        feed_container = soup.find('div',id='feed_container')
#        print feed_container
#        return feed_container




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    with app.app_context():
        #    with app.test_request_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    if request.method == 'POST':
        if not signupForm.validate():
            return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm)
        else:
            newuser = User(signupForm.username.data, signupForm.email.data, signupForm.password.data)
            newuser.created_at = datetime.utcnow()
            db.session.add(newuser)
            db.session.commit()

            session['username'] = newuser.username
            session['email'] = newuser.email
            session['logged_in'] = True
            session['user_id'] = newuser.id
            session['is_company'] = False

            return redirect(url_for('main'))


    if request.method == 'GET':
        return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm)

@app.route('/company_signup', methods=['GET','POST'])
def company_signup():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    if request.method == 'POST':
        if not companySignupForm.validate():
            return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm)
        else :
            if companySignupForm.validate_on_submit():

                filename = secure_filename(companySignupForm.filename.data.filename)
                if utils.allowedFile(filename):
                    print companySignupForm.pros_category.data

                    newuser = User(companySignupForm.username.data, companySignupForm.email.data, companySignupForm.password.data)
                    newuser.level = 2
                    newuser.created_at = datetime.utcnow()
                    db.session.add(newuser)
                    db.session.commit()

                    directory_url = os.path.join(app.config['UPLOAD_FOLDER'],newuser.email)
                    utils.createDirectory(directory_url)
                    file_path = os.path.join(directory_url,filename)
                    companySignupForm.filename.data.save(file_path)
                    image = Image(file_path)
                    image.user_id = newuser.id
                    db.session.add(image)
                    db.session.commit()
                    newcompany = Company(companySignupForm.introduction.data, companySignupForm.address.data, companySignupForm.tel.data, companySignupForm.website.data, newuser.id)
                    newcompany.image_id = image.id
                    db.session.add(newcompany)
                    db.session.commit()

                    for category_data in companySignupForm.pros_category.data:
                        cur_pros_category_id = int(category_data)
                        new_company_has_pros_category = Company_has_pros_category(newcompany.id,cur_pros_category_id)
                        db.session.add(new_company_has_pros_category)
                        db.session.commit()


                    session['username']     = newuser.username
                    session['email']        = newuser.email
                    session['logged_in']    = True
                    session['user_id']      = newuser.id
                    session['is_company'] = True

                    return redirect(url_for('main'))
    if request.method == 'GET':
        return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm)




@app.route('/signin',methods=['GET','POST'])
def signin():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    if request.method == 'POST':
        if not signinForm.validate():
            return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm)
        else :
            user = User.query.filter_by(email=signinForm.email.data.lower()).first()
            session['email'] = signinForm.email.data
            session['username'] = user.username
            session['logged_in'] = True
            session['user_id'] = user.id
            if user.level == 1:
                session['is_company'] = False
            elif user.level == 2:
                session['is_company'] = True

            return redirect(url_for('main'))
    elif request.method == 'GET':
        return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm)


@app.route('/signout')
def signout():
    if 'logged_in' not in session:
        return redirect(url_for('main'))
    session.pop('email', None)
    session.pop('username', None)
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('is_company',None)
    session.pop('project_id',None)
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
                feed.feed_category_id = int(writeFeedForm.feed_category.data)
                db.session.add(feed)
                db.session.commit()
            return redirect(url_for('main'))
    elif request.method == 'GET':
        return render_template('write_feed.html',writeFeedForm=writeFeedForm)

def merge_feed_for_project(createProjectForm):
    user = User.query.filter_by(email=session['email'].lower()).first()
    company = Company.query.filter_by(user_id=user.id).first()
    current_time = datetime.utcnow()
    one_minute_ago = current_time - timedelta(minutes=2)
    feeds = Feed.query.filter_by(user_id=user.id).filter(Feed.created_at > one_minute_ago).order_by(Feed.created_at.asc()).all()
    if len(feeds) == 0:
        return -1

    not_merged_feeds = []
    for feed in feeds:
        project_has_feed = Project_has_feed.query.filter_by(feed_id=feed.id).all()
        if len(project_has_feed) == 0:
            not_merged_feeds.append(feed)

    if len(not_merged_feeds) != 0:
        cur_feed = not_merged_feeds[0]
        project = Project(cur_feed.title,company.id,cur_feed.image_id, datetime.utcnow(),cur_feed.body,createProjectForm.project_credit.data)
        db.session.add(project)
        db.session.commit()
        for feed in not_merged_feeds:
            project_has_feed = Project_has_feed(project.id,feed.id)
            db.session.add(project_has_feed)
            db.session.commit()
        return project.id


@app.route('/create_project',methods=['GET','POST'])
def create_project():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
        createProjectForm = CreateProjectForm()


    if request.method == 'POST':
        if not createProjectForm.validate():
            return render_template('create_project.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm, \
                                   createProjectForm=createProjectForm)
        if request.files:
            file = request.files['file']
            filename = secure_filename(file.filename)

            user = User.query.filter_by(email=session['email'].lower()).first()
            company = Company.query.filter_by(user_id=user.id).first()
            if utils.allowedFile(filename):
                directory_url = os.path.join(app.config['UPLOAD_FOLDER'],session['email'])
                utils.createDirectory(directory_url)
                file_path = os.path.join(directory_url,filename)
                file.save(file_path)
                image = Image(file_path)
                image.user_id = user.id
                db.session.add(image)
                db.session.commit()
                feed = Feed(createProjectForm.project_name.data,createProjectForm.project_body.data,datetime.utcnow())
                feed.user_id = user.id
                feed.image_id = image.id
                feed.feed_category_id = 0
                db.session.add(feed)
                db.session.commit()
                return redirect(url_for('create_project'))
        else:
            project_id = merge_feed_for_project(createProjectForm)
            feeds_id = Project_has_feed.query.filter_by(project_id=project_id).order_by(Project_has_feed.feed_id.asc()).all()
            return redirect(url_for('project_edit',feed_id=feeds_id[0].feed_id))
            #return redirect(url_for('project_detail',project_id=project_id))
    elif request.method == 'GET':
        return render_template('create_project.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           createProjectForm=createProjectForm)
    return redirect(url_for('create_project'))

@app.route('/project_edit/<int:feed_id>',methods=['GET','POST'])
def project_edit(feed_id):
    with app.app_context():
        writeFeedForm = ProjectEditForm()

    feed = Feed.query.filter_by(id=feed_id).first()
    writeFeedForm.body.data = feed.body
    image = Image.query.filter_by(id=feed.image_id).first()
    image_path = utils.get_image_path(image.image_path)

    project_has_feed = Project_has_feed.query.filter_by(feed_id=feed.id).first()
    project = Project.query.filter_by(id=project_has_feed.project_id).first()
    project_has_feeds = Project_has_feed.query.filter_by(project_id=project.id).order_by(Project_has_feed.feed_id.asc()).all()
    feeds_id = []
    for project_has_feed in project_has_feeds:
        feeds_id.append(project_has_feed.feed_id)
    prev = -1
    next = -1
    idx = 0
    for i in xrange(len(feeds_id)):
        if feeds_id[i] == feed_id:
            idx = i
    if idx != 0 :
        prev = feeds_id[idx-1]
    if idx != len(feeds_id)-1:
        next = feeds_id[idx+1]
    ret = {
        'feed': feed,
        'prev': prev,
        'next': next,
        'image_path': image_path,
        'project_id': project.id
    }
    if request.method == 'POST':
        return render_template('project_edit.html',writeFeedForm=writeFeedForm,ret=ret)
    elif request.method == 'GET':
        return render_template('project_edit.html',writeFeedForm=writeFeedForm,ret=ret)

@app.route('/make_project',methods=['GET','POST'])
def make_project():
    project_id = session['project_id']
    with app.app_context():
        writeFeedForm = WriteFeedForm()
        makeProjectForm = MakeProjectForm()

    if request.method == 'POST':
        if project_id == 0: # first make project
            if not makeProjectForm.validate():
                print 'not validate'
                return render_template('make_project.html',writeFeedForm=writeFeedForm,makeProjectForm=makeProjectForm,project_id=project_id)
            else :
                if makeProjectForm.validate_on_submit():
                    user = User.query.filter_by(email=session['email'].lower()).first()
                    company = Company.query.filter_by(user_id=user.id).first()

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
                    feed.feed_category_id = int(writeFeedForm.feed_category.data)
                    db.session.add(feed)
                    db.session.commit()
                    project = Project(makeProjectForm.project_name.data,company.id,image.id, datetime.utcnow(),makeProjectForm.project_body, makeProjectForm.project_credit)
                    db.session.add(project)
                    db.session.commit()
                    project_has_feed = Project_has_feed(project.id,feed.id)
                    db.session.add(project_has_feed)
                    db.session.commit()

                    session['project_id'] = project.id
                    return redirect(url_for('make_project'))
        elif project_id != 0:
            if not writeFeedForm.validate():
                print 'not validate'
                return render_template('make_project.html',writeFeedForm=writeFeedForm,makeProjectForm=makeProjectForm,project_id=project_id)
            else :
                if writeFeedForm.validate_on_submit():
                    user = User.query.filter_by(email=session['email'].lower()).first()
                    company = Company.query.filter_by(user_id=user.id).first()

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
                    feed.feed_category_id = int(writeFeedForm.feed_category.data)
                    db.session.add(feed)
                    db.session.commit()
                    project_has_feed = Project_has_feed(project_id,feed.id)
                    db.session.add(project_has_feed)
                    db.session.commit()

                    return redirect(url_for('make_project'))

#            return render_template('make_project.html',makeProjectForm=makeProjectForm,project_id=project_id)
    elif request.method == 'GET':
        return render_template('make_project.html',writeFeedForm=writeFeedForm,makeProjectForm=makeProjectForm,project_id=project_id)



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

@app.route('/company_feed_detail/<int:feed_id>',methods=['GET','POST'])
def company_feed_detail(feed_id):
    with app.app_context():
        commentForm = CommentForm()
    feed = Feed.query.filter_by(id=feed_id).first()
    image = Image.query.filter_by(id=feed.image_id).first()
    image_path = utils.get_image_path(image.image_path)
    project_id = Project_has_feed.query.filter_by(feed_id=feed.id).first().project_id
    project = Project.query.filter_by(id=project_id).first()
    company = Company.query.filter_by(id=project.company_id).first()
    user = User.query.filter_by(id=company.user_id).first()
    all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()

    ret = {
        'feed': feed,
        'project': project,
        'user': user,
        'all_comments': all_comments,
        'image_path': image_path,
        'company': company
    }
    if request.method == 'GET':
        return render_template('company_feed_detail.html',commentForm=commentForm,ret=ret)
    elif request.method == 'POST':
        if not commentForm.validate():
            return render_template('company_feed_detail.html',commentForm=commentForm,ret=ret)
        if commentForm.validate_on_submit():
            comment = Comment(commentForm.body.data, datetime.utcnow())
            comment_user = User.query.filter_by(email=session['email'].lower()).first()
            comment.user_id = comment_user.id
            comment.feed_id = feed.id
            db.session.add(comment)
            db.session.commit()
            ret['all_comments'] = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()
        return redirect(url_for('company_feed_detail',feed_id=feed.id))

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

@app.route('/user_portfolio/<int:user_id>')
def user_portfolio(user_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()
    feeds = Feed.query.filter_by(user_id=user.id).order_by(Feed.created_at.desc()).all()
    ret_feeds = []

    for feed in feeds:
        d = {}
        image = Image.query.filter_by(id=feed.image_id).first()
        image_path = utils.get_image_path(image.image_path)
        all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()
        d['image_path'] = image_path
        d['user'] = user
        d['feed'] = feed
        d['number_of_comment'] = len(all_comments)
        ret_feeds.append(d)
    return render_template('user_portfolio.html',user=user,signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,feeds=ret_feeds)

@app.route('/company_portfolio/<int:user_id>')
def company_portfolio(user_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()
    company = Company.query.filter_by(user_id=user.id).first()
    t_projects = Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).all()
    projects = []
    for project in t_projects:
        cur_image = Image.query.filter_by(id=project.image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'project': project,
            'image_path': cur_image_path
        }
        projects.append(d)
    image   = Image.query.filter_by(id=company.image_id).first()
    image_path = utils.get_image_path(image.image_path)
    ret = {
        'user': user,
        'company': company,
        'projects': projects,
        'image_path': image_path
    }

    return render_template('company_portfolio.html', signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           ret=ret)

@app.route('/project_detail/<int:project_id>')
def project_detail(project_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    project = Project.query.filter_by(id=project_id).first()
    company = Company.query.filter_by(id=project.company_id).first()
    company_image   = Image.query.filter_by(id=company.image_id).first()
    company_image_path = utils.get_image_path(company_image.image_path)
    projects = Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).all()
    user = User.query.filter_by(id=company.user_id).first()
    project_has_feeds = Project_has_feed.query.filter_by(project_id=project_id).all()
    feeds = []
    for project_has_feed in project_has_feeds:
        cur_feed_id = project_has_feed.feed_id
        cur_feed = Feed.query.filter_by(id=cur_feed_id).first()
        image = Image.query.filter_by(id=cur_feed.image_id).first()
        image_path = utils.get_image_path(image.image_path)
        all_comments = Comment.query.filter_by(feed_id=cur_feed.id).order_by(Comment.created_at.desc()).all()
        d = {
            "feed": cur_feed,
            "image_path": image_path,
            "number_of_comment": len(all_comments)
        }
        feeds.append(d)
    feed_introduction = ''
    if len(feeds) != 0:
        feed_introduction = feeds[0]['feed'].body
    ret = {
        'user': user,
        'company': company,
        'project': project,
        'projects': projects,
        'feeds': feeds,
        'feed_introduction': feed_introduction,
        'image_path': company_image_path
    }
    return render_template('project_detail.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           ret=ret)


@app.route('/product_detail/<int:product_id>')
def product_detail(product_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    return render_template('product_detail.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm)

@app.route('/find_pros/')
def find_pros():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    ret_pros = []
    users = User.query.filter_by(level=2).order_by(User.created_at.desc()).all()
    for user in users:
        d = {}
        company = Company.query.filter_by(user_id=user.id).first()
        image = Image.query.filter_by(id=company.image_id).first()
        image_path = utils.get_image_path(image.image_path)
        d['user'] = user
        d['company'] = company
        d['image_path'] = image_path
        ret_pros.append(d)

    return render_template('find_pros.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,ret_pros=ret_pros,pros_size=len(ret_pros))

@app.route('/find_pros/<int:pros_category_id>')
def find_pros_detail(pros_category_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    ret_pros = []
    users = User.query.filter_by(level=2).order_by(User.created_at.desc()).all()
    for user in users:
        d = {}
        company = Company.query.filter_by(user_id=user.id).first()
        company_has_pros_categorys = Company_has_pros_category.query.filter_by(company_id=company.id).all()
        ok = False
        for company_has_pros_category in company_has_pros_categorys:
            if int(company_has_pros_category.pros_category_id) == pros_category_id:
                ok = True
        if not ok:
            continue
        image = Image.query.filter_by(id=company.image_id).first()
        image_path = utils.get_image_path(image.image_path)
        d['user'] = user
        d['company'] = company
        d['image_path'] = image_path
        ret_pros.append(d)

    return render_template('find_pros.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,ret_pros=ret_pros,pros_size=len(ret_pros))


@app.route('/photos/',methods=['GET','POST'])
def photos():
    feed_category_id = 0
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    if request.method == 'GET':
        offset = 10
        feeds = Feed.query.order_by(Feed.created_at.desc()).limit(offset).all()
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

        return render_template('photos.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm, feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id)
    elif request.method == 'POST':
        offset = int(request.form['offset'])
        feeds = Feed.query.order_by(Feed.created_at.desc()).limit(offset).all()
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

        html_code = render_template('photos.html', signupForm=signupForm, signinForm=signinForm,companySignupForm=companySignupForm ,feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id)
        return html_code

@app.route('/photos/<int:feed_category_id>')
def photos_detail(feed_category_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    if request.method == 'GET':
        offset = 10
        feeds = Feed.query.filter_by(feed_category_id=feed_category_id).order_by(Feed.created_at.desc()).limit(offset).all()
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

        return render_template('photos.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm, feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id)

    elif request.method == 'POST':
        offset = int(request.form['offset'])
        feeds = Feed.query.filter_by(feed_category_id=feed_category_id).order_by(Feed.created_at.desc()).limit(offset).all()
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

        html_code = render_template('photos.html', signupForm=signupForm, signinForm=signinForm,companySignupForm=companySignupForm ,feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id)
        return html_code

