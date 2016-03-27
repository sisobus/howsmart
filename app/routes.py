# -*- coding:utf-8 -*-
from flask import Flask, url_for
from werkzeug import secure_filename
from werkzeug.datastructures import ImmutableMultiDict 
import utils
import os
import time
from sqlalchemy import func

from config import UPLOAD_FOLDER, HOWSMART_DATABASE_URI, HOWSMART_SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']   = HOWSMART_DATABASE_URI
app.config['SECRET_KEY']                = HOWSMART_SECRET_KEY
app.config['UPLOAD_FOLDER']             = UPLOAD_FOLDER

from models import db, User, Feed, Image, Comment, Company, Project, Project_has_feed, Pros_category, Company_has_pros_category, Feed_category, Product, Product_has_image, Shop_category, User_like_feed, Follow, Status, Tag, Project_type_category, Style_category, Project_hash_tag, Product_hash_tag, Blog_post, Blog_post_comment, User_save_feed, User_save_post, User_save_product, User_profile

db.init_app(app)

import json
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask import get_flashed_messages
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
from forms import SignupForm, SigninForm, WriteFeedForm, CommentForm, CompanySignupForm, MakeProjectForm, CreateProjectForm, ProjectEditForm, CreateProductForm, CompanySearchForm, FindProsForm, AddTagForm
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def get_user_profile_image_path(user):
    user_profile_image_path = ''
    user_profile = User_profile.query.filter_by(user_id=user.id).order_by(User_profile.created_at.desc()).first()
    if user_profile:
        image = Image.query.filter_by(id=user_profile.image_id).first()
        user_profile_image_path = utils.get_image_path(image.image_path)

    return user_profile_image_path 

def get_feed_information(feeds):
    ret = []
    for feed in feeds:
        d = {}
        image = Image.query.filter_by(id=feed.image_id).first()
        image_path = utils.get_image_path(image.image_path)
        user = User.query.filter_by(id=feed.user_id).first()
        all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.asc()).all()

        comments_dict_list = []
        for all_comment in all_comments:
            comment_user = User.query.filter_by(id=all_comment.user_id).first()
            cur = {
                    'comment': all_comment,
                    'user': comment_user
                    }
            comments_dict_list.append(cur)

        all_likes = User_like_feed.query.filter_by(feed_id=feed.id).all()
        is_user_like = False
        if 'user_id' in session:
            if User_like_feed.query.filter_by(user_id=session['user_id']).filter_by(feed_id=feed.id).first():
                is_user_like = True

        d['image_path'] = image_path
        d['user'] = user
        d['feed'] = feed
        d['number_of_comment'] = len(all_comments)
        d['all_comments'] = comments_dict_list
        d['number_of_like'] = len(all_likes)
        d['is_user_like'] = is_user_like
        ret.append(d)
    return ret

def get_blog_post_information(posts):
    ret = []
    for post in posts:
        d = {}
        image = Image.query.filter_by(id=post.image_id).first()
        image_path = utils.get_image_path(image.image_path)
        user = User.query.filter_by(id=post.user_id).first()
        blog_post_comments = Blog_post_comment.query.filter_by(blog_post_id=post.id).order_by(Blog_post_comment.created_at.asc()).all()

        comments_dict_list = []
        for all_comment in blog_post_comments:
            comment_user = User.query.filter_by(id=all_comment.user_id).first()
            user_profile_image_path = get_user_profile_image_path(comment_user)
            cur = {
                    'comment': all_comment,
                    'user': comment_user,
                    'user_profile_image_path': user_profile_image_path 
                    }
            comments_dict_list.append(cur)
        d['image_path'] = image_path
        d['user'] = user
        d['post'] = post
        d['number_of_comment'] = len(blog_post_comments)
        ret.append(d)
    return ret

        
        

@app.route('/',methods=['GET','POST'])
def main():
    session['project_id'] = 0

    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    banner_feeds = []
    projects = Project.query.order_by(Project.created_at.desc()).all()
    for project in projects:
        project_has_feed = Project_has_feed.query.filter_by(project_id=project.id).order_by(Project_has_feed.feed_id.asc()).first()
        feed = Feed.query.filter_by(id=project_has_feed.feed_id).first()
        banner_feeds.append(feed)
    ret_banner_feeds = get_feed_information(banner_feeds)
    all_feed_count = Feed.query.count()
    if request.method == 'GET':
        offset = 10
        companies = Company.query.order_by(Company.id.desc()).all()
        feeds = []
        for company in companies:
            cur_project = Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).first()
            if not cur_project:
                continue
            cur_feed_id = Project_has_feed.query.filter_by(project_id=cur_project.id).order_by(Project_has_feed.feed_id.asc()).first().feed_id
            cur_feed = Feed.query.filter_by(id=cur_feed_id).first()
            feeds.append(cur_feed)
        ret_feeds = get_feed_information(feeds)
        ret_feeds = sorted(ret_feeds, key=lambda k: k['feed'].created_at, reverse=True)
        blog_posts = Blog_post.query.order_by(Blog_post.created_at.desc()).all()
        posts = get_blog_post_information(blog_posts)

        return render_template('main.html', signupForm=signupForm, signinForm=signinForm, \
                               companySignupForm=companySignupForm, feeds=ret_feeds, offset=offset,ret_banner_feeds=ret_banner_feeds,posts=posts)

    elif request.method == 'POST':
        offset = int(request.form['offset'])
        feeds = Feed.query.order_by(Feed.created_at.desc()).limit(offset).all()
        ret_feeds = get_feed_information(feeds)
        html_code = render_template('main.html', signupForm=signupForm, signinForm=signinForm,\
                                    companySignupForm=companySignupForm ,feeds=ret_feeds, offset=offset,all_feed_count=all_feed_count,ret_banner_feeds=ret_banner_feeds)
        return html_code

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    with app.app_context():
        #    with app.test_request_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    if request.method == 'POST':
        if not signupForm.validate():
            return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm,offset=10)
        else:
            newuser = User(signupForm.username.data, signupForm.email.data, signupForm.password.data)
            newuser.created_at = datetime.utcnow()
            newuser.status_id = 1
            db.session.add(newuser)
            db.session.commit()

            user_profile = User_profile(newuser.id, 565, datetime.utcnow())
            db.session.add(user_profile)
            db.session.commit()

            session['username'] = newuser.username
            session['email'] = newuser.email
            session['logged_in'] = True
            session['user_id'] = newuser.id
            session['is_company'] = False
            session['user_profile_image_path'] = get_user_profile_image_path(newuser)

            return redirect(url_for('main'))

    if request.method == 'GET':
        return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm,offset=10)

@app.route('/company_signup', methods=['GET','POST'])
def company_signup():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    if request.method == 'POST':
        if not companySignupForm.validate():
            return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm,offset=10)
        else :
            if companySignupForm.validate_on_submit():

                filename = secure_filename(companySignupForm.filename.data.filename)
                if utils.allowedFile(filename):
                    print companySignupForm.pros_category.data

                    newuser = User(companySignupForm.username.data, companySignupForm.email.data, companySignupForm.password.data)
                    newuser.level = 2
                    newuser.created_at = datetime.utcnow()
                    newuser.status_id = 1
                    db.session.add(newuser)
                    db.session.commit()
                    print 'complete: new user add'

                    user_profile = User_profile(newuser.id, 565, datetime.utcnow())
                    db.session.add(user_profile)
                    db.session.commit()

                    directory_url = os.path.join(app.config['UPLOAD_FOLDER'],newuser.email)
                    utils.createDirectory(directory_url)
                    file_path = os.path.join(directory_url,filename)
                    companySignupForm.filename.data.save(file_path)
                    image = Image(file_path)
                    image.user_id = newuser.id
                    image.created_at = datetime.utcnow()
                    db.session.add(image)
                    db.session.commit()
                    print 'complete: new image add'
                    newcompany = Company(companySignupForm.introduction.data, companySignupForm.address.data, companySignupForm.tel.data, companySignupForm.website.data, newuser.id, companySignupForm.company_si.data, companySignupForm.company_gu.data, companySignupForm.company_dong.data)
                    newcompany.image_id = image.id
                    newcompany.status_id = 1
                    db.session.add(newcompany)
                    db.session.commit()
                    print 'complete: new company add'

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
                    session['user_profile_image_path'] = get_user_profile_image_path(newuser)
                    print 'complete: new session add'
                    
                    #return redirect(url_for('company_portfolio',user_id=newuser.id))
                    return redirect(url_for('main'))
    if request.method == 'GET':
        return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm,offset=10)

@app.route('/signin',methods=['GET','POST'])
def signin():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    if request.method == 'POST':
        if not signinForm.validate():
            return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm,offset=10)
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
            session['user_profile_image_path'] = get_user_profile_image_path(user)

            return redirect(url_for('main'))
    elif request.method == 'GET':
        return render_template('main.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm,offset=10)


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
    session.pop('user_profile_image_path',None)
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
                    image.created_at = datetime.utcnow()
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
        project.status_id = 1
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
        user = User.query.filter_by(email=session['email'].lower()).first()
        company = Company.query.filter_by(user_id=user.id).first()
        if request.files:
            files = request.files
            for file_key in files:
                file = request.files[file_key]
                filename = secure_filename(file.filename)
                if utils.allowedFile(filename):
                    directory_url = os.path.join(app.config['UPLOAD_FOLDER'],session['email'])
                    utils.createDirectory(directory_url)
                    project_count = Project.query.filter_by(company_id=company.id).count()
                    directory_url = os.path.join(directory_url,str(project_count+1))
                    utils.createDirectory(directory_url)
                    file_path = os.path.join(directory_url,filename)
                    file.save(file_path)
                    image = Image(file_path)
                    image.user_id = user.id
                    image.created_at = datetime.utcnow()
                    db.session.add(image)
                    db.session.commit()
                    feed = Feed('pre','pre',datetime.utcnow())
                    feed.user_id = user.id
                    feed.image_id = image.id
                    feed.feed_category_id = 1
                    feed.status_id = 1
                    db.session.add(feed)
                    db.session.commit()
            return render_template('create_project.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm, \
                                   createProjectForm=createProjectForm)
        if not createProjectForm.validate():
            return render_template('create_project.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm, \
                                   createProjectForm=createProjectForm)
        project_id = merge_feed_for_project(createProjectForm)
        project = Project.query.filter_by(id=project_id).first()
        project.project_name = createProjectForm.project_name.data
        project.project_body = createProjectForm.project_body.data
        if createProjectForm.project_type_category.data:
            project.project_type_category_id = createProjectForm.project_type_category.data
        if createProjectForm.project_si.data:
            project.project_si = createProjectForm.project_si.data
        if createProjectForm.project_gu.data:
            project.project_gu = createProjectForm.project_gu.data
        if createProjectForm.project_dong.data:
            project.project_dong = createProjectForm.project_dong.data
        if createProjectForm.project_style_category.data:
            project.style_category_id = createProjectForm.project_style_category.data
        if createProjectForm.project_area.data:
            project.project_area = createProjectForm.project_area.data
        if createProjectForm.project_location.data:
            project.project_location = createProjectForm.project_location.data
        if createProjectForm.hash_tag.data:
            t_tags = createProjectForm.hash_tag.data.split('#')
            for t_tag in t_tags:
                tt_tag = t_tag.strip()
                if len(tt_tag) == 0:
                    continue
                project_hash_tag = Project_hash_tag(tt_tag,project.id)
                db.session.add(project_hash_tag)
                db.session.commit()
        db.session.commit()
        feeds_id = Project_has_feed.query.filter_by(project_id=project_id).order_by(Project_has_feed.feed_id.asc()).all()
        for feed_id in feeds_id:
            feed = Feed.query.filter_by(id=feed_id.feed_id).first()
            feed.title = createProjectForm.project_name.data
            feed.body = createProjectForm.project_body.data
            db.session.commit()
        return redirect(url_for('project_edit',feed_id=feeds_id[0].feed_id))
    elif request.method == 'GET':
        return render_template('create_project.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           createProjectForm=createProjectForm)
    return redirect(url_for('create_project'))

def merge_image_for_product(createProductForm):
    user = User.query.filter_by(email=session['email'].lower()).first()
    company = Company.query.filter_by(user_id=user.id).first()
    current_time = datetime.utcnow()
    one_minute_ago = current_time - timedelta(minutes=1)
    images = Image.query.filter_by(user_id=user.id).filter(Image.created_at > one_minute_ago).order_by(Image.created_at.asc()).all()
    if len(images) == 0:
        return -1

    not_merged_images = []
    for image in images:
        product_has_image  = Product_has_image.query.filter_by(image_id=image.id).all()
        if len(product_has_image) == 0:
            not_merged_images.append(image)

    if len(not_merged_images) != 0:
        product = Product(createProductForm.product_name.data,int(createProductForm.product_price.data),createProductForm.product_color.data,\
                          createProductForm.product_desc.data,createProductForm.product_size.data,createProductForm.product_model_name.data,\
                          createProductForm.product_meterial.data,int(createProductForm.shop_category.data),user.id,datetime.utcnow())
        product.product_sale_price = product.price
        product.status_id = 1
        db.session.add(product)
        db.session.commit()
        for image in not_merged_images:
            product_has_image = Product_has_image(product.id,image.id)
            db.session.add(product_has_image)
            db.session.commit()
        return product.id

@app.route('/create_product',methods=['GET','POST'])
def create_product():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
        createProductForm = CreateProductForm()

    if request.method == 'POST':
        user = User.query.filter_by(email=session['email'].lower()).first()
        company = Company.query.filter_by(user_id=user.id).first()
        if request.files:
            files = request.files
            for file_key in files:
                file = request.files[file_key]
                filename = secure_filename(file.filename)
                if utils.allowedFile(filename):
                    directory_url = os.path.join(app.config['UPLOAD_FOLDER'],session['email'])
                    utils.createDirectory(directory_url)
                    file_path = os.path.join(directory_url,filename)
                    file.save(file_path)
                    image = Image(file_path)
                    image.user_id = user.id
                    image.created_at = datetime.utcnow()
                    db.session.add(image)
                    db.session.commit()

            return render_template('create_product.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm, \
                                   createProductForm=createProductForm)
        if not createProductForm.validate():
            return render_template('create_product.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm, \
                                   createProductForm=createProductForm)
        product_id = merge_image_for_product(createProductForm)
        product = Product.query.filter_by(id=product_id).first()
        if createProductForm.product_style_category.data:
            product.style_category_id = createProductForm.product_style_category.data
        if createProductForm.hash_tag.data:
            t_tags = createProductForm.hash_tag.data.split('#')
            for t_tag in t_tags:
                tt_tag = t_tag.strip()
                if len(tt_tag) == 0:
                    continue
                product_hash_tag = Product_hash_tag(tt_tag,product.id)
                db.session.add(product_hash_tag)
                db.session.commit()

            
        return redirect(url_for('company_portfolio_shop',user_id=user.id))
    elif request.method == 'GET':
        return render_template('create_product.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm, \
                               createProductForm=createProductForm)
    return redirect(url_for('create_product'))

@app.route('/project_edit/<int:feed_id>',methods=['GET','POST'])
def project_edit(feed_id):
    with app.app_context():
        writeFeedForm = ProjectEditForm()
    
    feed = Feed.query.filter_by(id=feed_id).first()
    image = Image.query.filter_by(id=feed.image_id).first()
    image_path = utils.get_image_path(image.image_path)
    if request.method == 'GET':
        writeFeedForm.body.data = feed.body

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

    tags = Tag.query.filter_by(feed_id=feed.id).all()
    ret = {
        'feed': feed,
        'prev': prev,
        'next': next,
        'image_path': image_path,
        'project_id': project.id,
        'tags': tags
    }
    if request.method == 'POST':
        cur_feed = Feed.query.filter_by(id=feed_id).first()
        cur_feed.title = writeFeedForm.title.data
        cur_feed.body = writeFeedForm.body.data
        if writeFeedForm.feed_category.data != "None" :
            cur_feed.feed_category_id = writeFeedForm.feed_category.data
        db.session.commit()
        return redirect(url_for('project_edit',feed_id=next))
#        return render_template('project_edit.html',writeFeedForm=writeFeedForm,ret=ret)
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
                        image.created_at = datetime.utcnow()
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
                        image.created_at = datetime.utcnow()
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
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    if request.args.get('previous_url'):
        session['previous_url'] = request.args.get('previous_url')
        print '@@#!@#!#'+request.args.get('previous_url')
    feed = Feed.query.filter_by(id=feed_id).first()
    feed_category = Feed_category.query.filter_by(id=feed.feed_category_id).first()
    feed_category_name = feed_category.category_name
    image = Image.query.filter_by(id=feed.image_id).first()
    image_path = utils.get_image_path(image.image_path)
    project_id = Project_has_feed.query.filter_by(feed_id=feed.id).first().project_id
    project = Project.query.filter_by(id=project_id).first()
    company = Company.query.filter_by(id=project.company_id).first()
    user = User.query.filter_by(id=company.user_id).first()
    user_profile_image_path = get_user_profile_image_path(user)
    all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()

    comments_dict_list = []
    for all_comment in all_comments:
        comment_user = User.query.filter_by(id=all_comment.user_id).first()
        cur = {
                'comment': all_comment,
                'user': comment_user,
                'user_profile_image_path': get_user_profile_image_path(comment_user)
                }
        comments_dict_list.append(cur)

    all_likes = User_like_feed.query.filter_by(feed_id=feed.id).all()
    is_user_like = False
    if 'user_id' in session:
        if User_like_feed.query.filter_by(user_id=session['user_id']).filter_by(feed_id=feed.id).first():
            is_user_like = True

    project_has_feeds = Project_has_feed.query.filter_by(project_id=project.id).order_by(Project_has_feed.feed_id.asc()).all()
    feeds_id = []
    other_feeds_in_same_project = []
    for project_has_feed in project_has_feeds:
        feeds_id.append(project_has_feed.feed_id)
        if len(other_feeds_in_same_project) < 4:
            cur_feed = Feed.query.filter_by(id=project_has_feed.feed_id).first()
            cur_image = Image.query.filter_by(id=cur_feed.image_id).first()
            cur_image_path = utils.get_image_path(cur_image.image_path)
            d = {
                'feed': cur_feed,
                'image_path': cur_image_path
            }
            other_feeds_in_same_project.append(d)
    other_projects = []
    for cur_project in Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).limit(4).all():
        cur_image = Image.query.filter_by(id=cur_project.image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'project': cur_project,
            'image_path': cur_image_path
        }
        other_projects.append(d)
    prev = -1
    next = -1
    idx = 0
    for i in xrange(len(feeds_id)):
        if feeds_id[i] == feed_id:
            idx = i
    if idx != 0 :
        prev = feeds_id[idx-1]
    elif idx == 0 :
        prev = feeds_id[-1]
    if idx != len(feeds_id)-1:
        next = feeds_id[idx+1]
    elif idx == len(feeds_id)-1:
        next = feeds_id[0]

    tags = Tag.query.filter_by(feed_id=feed.id).all()

    ret = {
        'feed': feed,
        'project': project,
        'user': user,
        'all_comments': comments_dict_list,
        'image_path': image_path,
        'company': company,
        'next_feed_id': next,
        'prev_feed_id': prev,
        'feed_category_name': feed_category_name,
        'other_feeds_in_same_project': other_feeds_in_same_project,
        'other_projects': other_projects,
        'number_of_like': len(all_likes),
        'is_user_like': is_user_like,
        'referrer': session['previous_url'] ,
        'tags': tags,
        'user_profile_image_path': user_profile_image_path
    }
    if request.method == 'GET':
        return render_template('company_feed_detail.html',commentForm=commentForm,ret=ret,signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm)
    elif request.method == 'POST':
        if not commentForm.validate():
            return render_template('company_feed_detail.html',commentForm=commentForm,ret=ret,signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm)
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
    number_of_follow = Follow.query.filter_by(to_user_id=user.id).count()
    number_of_from_follow = Follow.query.filter_by(from_user_id=user.id).count()
    is_user_follow = False
    if 'user_id' in session:
        if Follow.query.filter_by(to_user_id=user.id).filter_by(from_user_id=session['user_id']).first():
            is_user_follow = True
    user_save_feeds = User_save_feed.query.filter_by(user_id=user.id).order_by(User_save_feed.id.desc()).all()
    number_of_projects = len(user_save_feeds)
    projects = []
    for user_save_feed in user_save_feeds:
        feed = Feed.query.filter_by(id=user_save_feed.feed_id).first()
        project_has_feed = Project_has_feed.query.filter_by(feed_id=feed.id).first()
        project = Project.query.filter_by(id=project_has_feed.project_id).first()
        cur_image = Image.query.filter_by(id=project.image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'project': project,
            'image_path': cur_image_path,
            'comment': user_save_feed.comment
        }
        projects.append(d)

    user_save_products = User_save_product.query.filter_by(user_id=user.id).order_by(User_save_product.id.desc()).all()
    number_of_products = len(user_save_products)
    products = []
    for user_save_product in user_save_products:
        product = Product.query.filter_by(id=user_save_product.product_id).first()
        cur_image_id = Product_has_image.query.filter_by(product_id=product.id).first().image_id
        cur_image = Image.query.filter_by(id=cur_image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'product': product,
            'image_path': cur_image_path,
            'comment': user_save_product.comment
        }
        products.append(d)
    user_save_posts = User_save_post.query.filter_by(user_id=user.id).order_by(User_save_post.id.desc()).all()
    number_of_posts= len(user_save_posts)
    posts = []
    for user_save_post in user_save_posts:
        blog_post = Blog_post.query.filter_by(id=user_save_post.post_id).first()
        cur_image = Image.query.filter_by(id=blog_post.image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'post': blog_post,
            'image_path': cur_image_path,
            'comment': user_save_post.comment
        }
        posts.append(d)

    user_profile_image_path = ''
    user_profile = User_profile.query.filter_by(user_id=user.id).order_by(User_profile.created_at.desc()).first()
    if user_profile:
        image = Image.query.filter_by(id=user_profile.image_id).first()
        user_profile_image_path = utils.get_image_path(image.image_path)

    ret = {
        'user': user,
        'number_of_follow': number_of_follow,
        'number_of_from_follow': number_of_from_follow,
        'is_user_follow': is_user_follow,
        'number_of_projects': number_of_projects,
        'projects': projects[:6],
        'number_of_products': number_of_products,
        'products': products[:6],
        'number_of_posts': number_of_posts,
        'posts': posts[:6],
        'user_profile_image_path': user_profile_image_path
            }

    return render_template('user_portfolio.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,ret=ret)

@app.route('/user_portfolio/<int:user_id>/project')
def user_portfolio_project(user_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()
    user_save_feeds = User_save_feed.query.filter_by(user_id=user.id).order_by(User_save_feed.id.desc()).all()
    number_of_projects = len(user_save_feeds)
    projects = []
    for user_save_feed in user_save_feeds:
        feed = Feed.query.filter_by(id=user_save_feed.feed_id).first()
        project_has_feed = Project_has_feed.query.filter_by(feed_id=feed.id).first()
        project = Project.query.filter_by(id=project_has_feed.project_id).first()
        cur_image = Image.query.filter_by(id=project.image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'project': project,
            'image_path': cur_image_path,
            'comment': user_save_feed.comment
        }
        projects.append(d)

    ret = {
        'user': user,
        'number_of_projects': number_of_projects,
        'projects': projects,
            }

    return render_template('user_portfolio_project.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,ret=ret)


@app.route('/user_portfolio/<int:user_id>/shop')
def user_portfolio_shop(user_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()

    user_save_products = User_save_product.query.filter_by(user_id=user.id).order_by(User_save_product.id.desc()).all()
    number_of_products = len(user_save_products)
    products = []
    for user_save_product in user_save_products:
        product = Product.query.filter_by(id=user_save_product.product_id).first()
        cur_image_id = Product_has_image.query.filter_by(product_id=product.id).first().image_id
        cur_image = Image.query.filter_by(id=cur_image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'product': product,
            'image_path': cur_image_path,
            'comment': user_save_product.comment
        }
        products.append(d)
    
    used_category = [ False for i in xrange(128) ]
    ret_category = utils.get_all_category()
    for category in ret_category:
        for second_category in category['child_categories']:
            if used_category[int(second_category['category_id'])]:
                second_category['used'] = True


    ret = {
        'user': user,
        'number_of_products': number_of_products,
        'products': products,
        'category': ret_category
            }

    return render_template('user_portfolio_shop.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,ret=ret)

@app.route('/user_portfolio/<int:user_id>/news')
def user_portfolio_news(user_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()
    user_save_posts = User_save_post.query.filter_by(user_id=user.id).order_by(User_save_post.id.desc()).all()
    number_of_posts= len(user_save_posts)
    posts = []
    for user_save_post in user_save_posts:
        blog_post = Blog_post.query.filter_by(id=user_save_post.post_id).first()
        cur_image = Image.query.filter_by(id=blog_post.image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'post': blog_post,
            'image_path': cur_image_path,
            'comment': user_save_post.comment
        }
        posts.append(d)

    ret = {
        'user': user,
        'number_of_posts': number_of_posts,
        'posts': posts,
            }

    return render_template('user_portfolio_news.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,ret=ret)



@app.route('/company_portfolio/<int:user_id>')
def company_portfolio(user_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()
    company = Company.query.filter_by(user_id=user.id).first()
    t_projects = Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).all()
    number_of_all_projects = len(t_projects)
    projects = []
    for project in t_projects:
        if 'is_company' in session and session['is_company']:
            if len(projects) >= 5:
                break
        else :
            if len(projects) >= 6:
                break
        cur_image = Image.query.filter_by(id=project.image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'project': project,
            'image_path': cur_image_path
        }
        projects.append(d)

    t_products = Product.query.filter_by(user_id=user.id).order_by(Product.created_at.desc()).all()
    number_of_all_products = len(t_products)
    products = []
    for t_product in t_products:
        if 'is_company' in session and session['is_company']:
            if len(products) >= 5:
                break
        else:
            if len(products) >= 6:
                break
        cur_image_id = Product_has_image.query.filter_by(product_id=t_product.id).first().image_id
        cur_image = Image.query.filter_by(id=cur_image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'product': t_product,
            'image_path': cur_image_path
        }
        products.append(d)

    image   = Image.query.filter_by(id=company.image_id).first()
    image_path = utils.get_image_path(image.image_path)

    number_of_follow = Follow.query.filter_by(to_user_id=user.id).count()
    number_of_from_follow = Follow.query.filter_by(from_user_id=user.id).count()
    is_user_follow = False
    if 'user_id' in session:
        if Follow.query.filter_by(to_user_id=user.id).filter_by(from_user_id=session['user_id']).first():
            is_user_follow = True

    user_profile_image_path = ''
    user_profile = User_profile.query.filter_by(user_id=user.id).order_by(User_profile.created_at.desc()).first()
    if user_profile:
        image = Image.query.filter_by(id=user_profile.image_id).first()
        user_profile_image_path = utils.get_image_path(image.image_path)


    ret = {
        'user': user,
        'company': company,
        'projects': projects,
        'products': products,
        'image_path': image_path,
        'number_of_projects': number_of_all_projects,
        'number_of_products': number_of_all_products,
        'number_of_follow': number_of_follow,
        'number_of_from_follow': number_of_from_follow,
        'is_user_follow': is_user_follow,
        'user_profile_image_path': user_profile_image_path
    }

    return render_template('company_portfolio.html', signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           ret=ret)
@app.route('/company_portfolio_edit/<int:user_id>')
def company_portfolio_edit(user_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()
    company = Company.query.filter_by(user_id=user.id).first()
    t_projects = Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).all()
    number_of_all_projects = len(t_projects)
    projects = []
    for project in t_projects:
        if 'is_company' in session and session['is_company']:
            if len(projects) >= 5:
                break
        else :
            if len(projects) >= 6:
                break
        cur_image = Image.query.filter_by(id=project.image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'project': project,
            'image_path': cur_image_path
        }
        projects.append(d)

    t_products = Product.query.filter_by(user_id=user.id).order_by(Product.created_at.desc()).all()
    number_of_all_products = len(t_products)
    products = []
    for t_product in t_products:
        if 'is_company' in session and session['is_company']:
            if len(products) >= 5:
                break
        else:
            if len(products) >= 6:
                break
        cur_image_id = Product_has_image.query.filter_by(product_id=t_product.id).first().image_id
        cur_image = Image.query.filter_by(id=cur_image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'product': t_product,
            'image_path': cur_image_path
        }
        products.append(d)

    image   = Image.query.filter_by(id=company.image_id).first()
    image_path = utils.get_image_path(image.image_path)

    number_of_follow = Follow.query.filter_by(to_user_id=user.id).count()
    number_of_from_follow = Follow.query.filter_by(from_user_id=user.id).count()
    is_user_follow = False
    if 'user_id' in session:
        if Follow.query.filter_by(to_user_id=user.id).filter_by(from_user_id=session['user_id']).first():
            is_user_follow = True

    ret = {
        'user': user,
        'company': company,
        'projects': projects,
        'products': products,
        'image_path': image_path,
        'number_of_projects': number_of_all_projects,
        'number_of_products': number_of_all_products,
        'number_of_follow': number_of_follow,
        'number_of_from_follow': number_of_from_follow,
        'is_user_follow': is_user_follow
    }

    return render_template('company_portfolio_edit.html', signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           ret=ret)

@app.route('/company_portfolio/<int:user_id>/project')
def company_portfolio_project(user_id):
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
            'image_path': cur_image_path,
            'number_of_feed': Project_has_feed.query.filter_by(project_id=project.id).count()
        }
        projects.append(d)
    image   = Image.query.filter_by(id=company.image_id).first()
    image_path = utils.get_image_path(image.image_path)
    user_profile_image_path = ''
    user_profile = User_profile.query.filter_by(user_id=user.id).order_by(User_profile.created_at.desc()).first()
    if user_profile:
        image = Image.query.filter_by(id=user_profile.image_id).first()
        user_profile_image_path = utils.get_image_path(image.image_path)

    ret = {
        'user': user,
        'company': company,
        'projects': projects,
        'image_path': image_path,
        'user_profile_image_path': user_profile_image_path
    }

    return render_template('company_portfolio_project.html', signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           ret=ret)

@app.route('/company_portfolio/<int:user_id>/shop')
def company_portfolio_shop(user_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()
    company = Company.query.filter_by(user_id=user.id).first()
    image   = Image.query.filter_by(id=company.image_id).first()
    image_path = utils.get_image_path(image.image_path)

    t_products = Product.query.filter_by(user_id=user.id).order_by(Product.created_at.desc()).all()
    products = []
    used_category = [ False for i in xrange(128) ]
    for t_product in t_products:
        used_category[t_product.shop_category_id] = True
        cur_image_id = Product_has_image.query.filter_by(product_id=t_product.id).first().image_id
        cur_image = Image.query.filter_by(id=cur_image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'product': t_product,
            'image_path': cur_image_path,
            'product_real_price': utils.convert_price_to_won(t_product.product_price),
            'product_real_sale_price': utils.convert_price_to_won(t_product.product_sale_price),
        }
        products.append(d)
    ret_category = utils.get_all_category()
    for category in ret_category:
        for second_category in category['child_categories']:
            if used_category[int(second_category['category_id'])]:
                second_category['used'] = True
    user_profile_image_path = ''
    user_profile = User_profile.query.filter_by(user_id=user.id).order_by(User_profile.created_at.desc()).first()
    if user_profile:
        image = Image.query.filter_by(id=user_profile.image_id).first()
        user_profile_image_path = utils.get_image_path(image.image_path)

    ret = {
        'user': user,
        'company': company,
        'products': products,
        'image_path': image_path,
        'category': ret_category,
        'user_profile_image_path': user_profile_image_path
    }

    return render_template('company_portfolio_shop.html', signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           ret=ret)

@app.route('/company_portfolio/<int:user_id>/shop/<int:shop_category_id>')
def company_portfolio_shop_detail(user_id,shop_category_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()
    company = Company.query.filter_by(user_id=user.id).first()
    image   = Image.query.filter_by(id=company.image_id).first()
    image_path = utils.get_image_path(image.image_path)


    used_category = [ False for i in xrange(128) ]
    t_products = Product.query.filter_by(user_id=user.id).order_by(Product.created_at.desc()).all()
    for t_product in t_products:
        used_category[t_product.shop_category_id] = True
    t_products = Product.query.filter_by(user_id=user.id).filter_by(shop_category_id=shop_category_id).order_by(Product.created_at.desc()).all()
    products = []
    for t_product in t_products:
        cur_image_id = Product_has_image.query.filter_by(product_id=t_product.id).first().image_id
        cur_image = Image.query.filter_by(id=cur_image_id).first()
        cur_image_path = utils.get_image_path(cur_image.image_path)
        d = {
            'product': t_product,
            'image_path': cur_image_path
        }
        products.append(d)
    ret_category = utils.get_all_category()
    for category in ret_category:
        for second_category in category['child_categories']:
            if used_category[int(second_category['category_id'])]:
                second_category['used'] = True
    user_profile_image_path = ''
    user_profile = User_profile.query.filter_by(user_id=user.id).order_by(User_profile.created_at.desc()).first()
    if user_profile:
        image = Image.query.filter_by(id=user_profile.image_id).first()
        user_profile_image_path = utils.get_image_path(image.image_path)

    ret = {
        'user': user,
        'company': company,
        'products': products,
        'image_path': image_path,
        'category': ret_category,
        'user_profile_image_path': user_profile_image_path
    }

    return render_template('company_portfolio_shop.html', signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           ret=ret)

@app.route('/company_portfolio/<int:user_id>/qna')
def company_portfolio_qna(user_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()
    company = Company.query.filter_by(user_id=user.id).first()
    image   = Image.query.filter_by(id=company.image_id).first()
    image_path = utils.get_image_path(image.image_path)

    user_profile_image_path = ''
    user_profile = User_profile.query.filter_by(user_id=user.id).order_by(User_profile.created_at.desc()).first()
    if user_profile:
        image = Image.query.filter_by(id=user_profile.image_id).first()
        user_profile_image_path = utils.get_image_path(image.image_path)
    ret = {
        'user': user,
        'company': company,
        'image_path': image_path,
        'user_profile_image_path': user_profile_image_path
    }

    return render_template('company_portfolio_qna.html', signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           ret=ret)

@app.route('/company_portfolio/<int:user_id>/review')
def company_portfolio_review(user_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    user = User.query.filter_by(id=user_id).first()
    company = Company.query.filter_by(user_id=user.id).first()
    image   = Image.query.filter_by(id=company.image_id).first()
    image_path = utils.get_image_path(image.image_path)

    user_profile_image_path = ''
    user_profile = User_profile.query.filter_by(user_id=user.id).order_by(User_profile.created_at.desc()).first()
    if user_profile:
        image = Image.query.filter_by(id=user_profile.image_id).first()
        user_profile_image_path = utils.get_image_path(image.image_path)
    ret = {
        'user': user,
        'company': company,
        'image_path': image_path,
        'user_profile_image_path': user_profile_image_path
    }

    return render_template('company_portfolio_review.html', signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
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

    user_profile_image_path = ''
    user_profile = User_profile.query.filter_by(user_id=user.id).order_by(User_profile.created_at.desc()).first()
    if user_profile:
        image = Image.query.filter_by(id=user_profile.image_id).first()
        user_profile_image_path = utils.get_image_path(image.image_path)
    ret = {
        'user': user,
        'company': company,
        'project': project,
        'projects': projects,
        'feeds': feeds,
        'feed_introduction': feed_introduction,
        'image_path': company_image_path,
        'user_profile_image_path': user_profile_image_path
    }
    return render_template('project_detail.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           ret=ret)

@app.route('/project_detail_edit/<int:project_id>')
def project_detail_edit(project_id):
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
    return render_template('project_detail_edit.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,\
                           ret=ret)



@app.route('/product_detail/<int:product_id>')
def product_detail(product_id):
    with app.app_context():
        comment = CommentForm()

    product = Product.query.filter_by(id=product_id).first()
    user = User.query.filter_by(id=product.user_id).first()
#    user = User.query.filter_by(email=session['email']).first()
    company = Company.query.filter_by(user_id=user.id).first()
    product_has_images = Product_has_image.query.filter_by(product_id=product.id).order_by(Product_has_image.image_id.asc()).all()
    image_paths = []
    for product_has_image in product_has_images:
        cur_image_id = product_has_image.image_id
        image = Image.query.filter_by(id=cur_image_id).first()
        image_path = utils.get_image_path(image.image_path)
        image_paths.append(image_path)
    colors = []
    for color in product.product_color.split(','):
        color = color.lstrip().rstrip()
        colors.append(color)

    other_image_paths = []
    for i in xrange(1,min(len(image_paths),5)):
        other_image_paths.append(image_paths[i])

    same_company_other_products = []
    t_products = Product.query.filter_by(user_id=user.id).order_by(Product.created_at.desc()).all()
    same_company_other_products_count = Product.query.filter_by(user_id=user.id).count()
    for t_product in t_products:
        if t_product.id == product_id:
            continue
        cur_product_image = Image.query.filter_by(id=Product_has_image.query.filter_by(product_id=t_product.id).first().image_id).first()
        cur_product_image_path = utils.get_image_path(cur_product_image.image_path)
        d = {
            'product': t_product,
            'product_real_price': utils.convert_price_to_won(t_product.product_price),
            'product_real_sale_price': utils.convert_price_to_won(t_product.product_sale_price),
            'image_path': cur_product_image_path
        }
        same_company_other_products.append(d)
        if len(same_company_other_products) == 4:
            break

    same_category_other_products = []
    t_products = Product.query.filter_by(shop_category_id=product.shop_category_id).order_by(Product.created_at.desc()).all()
    same_category_other_products_count = Product.query.filter_by(shop_category_id=product.shop_category_id).count()
    for t_product in t_products:
        if t_product.id == product_id:
            continue
        cur_product_image = Image.query.filter_by(id=Product_has_image.query.filter_by(product_id=t_product.id).first().image_id).first()
        cur_product_image_path = utils.get_image_path(cur_product_image.image_path)
        d = {
            'product': t_product,
            'product_real_price': utils.convert_price_to_won(t_product.product_price),
            'product_real_sale_price': utils.convert_price_to_won(t_product.product_sale_price),
            'image_path': cur_product_image_path
        }
        same_category_other_products.append(d)
        if len(same_category_other_products) == 4:
            break

    shop_category_id = product.shop_category_id
    shop_category_name = utils.get_shop_category_dictionary()[shop_category_id]

    ret = {
        'user': user,
        'company': company,
        'product': product,
        'product_real_price': utils.convert_price_to_won(product.product_price),
        'product_real_sale_price': utils.convert_price_to_won(product.product_sale_price),
        'image_paths': image_paths,
        'colors': colors,
        'other_image_paths': other_image_paths,
        'same_company_other_products': same_company_other_products,
        'same_company_other_products_count': same_company_other_products_count,
        'same_category_other_products': same_category_other_products,
        'same_category_other_products_count': same_category_other_products_count,
        'shop_category_id': shop_category_id,
        'shop_category_name': shop_category_name
    }
    return render_template('product_detail.html',ret=ret)

@app.route('/find_pros/',methods=['GET','POST'])
def find_pros():
    pros_category_id = 0
    pros_category_name = '전체'
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
        companySearchForm = CompanySearchForm()
        findProsForm = FindProsForm()

    if request.method == 'GET':
        ret_pros = []
        users = User.query.filter_by(level=2).order_by(User.created_at.desc()).all()
        for user in users:
            d = {}
            company = Company.query.filter_by(user_id=user.id).first()
            project = Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).all()
            image = Image.query.filter_by(id=company.image_id).first()
            image_path = utils.get_image_path(image.image_path)
            if len(project) == 0:
                d['last_project_created'] = user.created_at
            else :
                d['last_project_created'] = project[0].created_at
                image = Image.query.filter_by(id=project[0].image_id).first()
                image_path = utils.get_image_path(image.image_path)
            d['user'] = user
            d['over_introduction'] = False
            if len(company.company_introduction) > 250:
                company.company_introduction = company.company_introduction[:250]
                d['over_introduction'] = True
            d['company'] = company
            d['image_path'] = image_path
            d['user_profile_image_path'] = get_user_profile_image_path(user)
            ret_pros.append(d)

        ret_pros = sorted(ret_pros, key=lambda k: k['last_project_created'], reverse=True)

        return render_template('find_pros.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,ret_pros=ret_pros,pros_size=len(ret_pros),pros_category_name=pros_category_name,findProsForm=findProsForm)
    elif request.method == 'POST':
        ret_pros = []
        if findProsForm.company_gu.data != u'전체':
            if findProsForm.company_dong.data == u'전체':
                companies = Company.query.filter_by(company_si=findProsForm.company_si.data).filter_by(company_gu=findProsForm.company_gu.data).all()
            elif findProsForm.company_dong.data != u'전체':
                companies = Company.query.filter_by(company_si=findProsForm.company_si.data).filter_by(company_gu=findProsForm.company_gu.data).filter_by(company_dong=findProsForm.company_dong.data).all()
        elif findProsForm.company_gu.data == u'전체':
            companies = Company.query.filter_by(company_si=findProsForm.company_si.data).all()

        for company in companies:
            d = {}
            user = User.query.filter_by(id=company.user_id).first()
            project = Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).all()
            image = Image.query.filter_by(id=company.image_id).first()
            image_path = utils.get_image_path(image.image_path)
            if len(project) == 0:
                d['last_project_created'] = user.created_at
            else :
                d['last_project_created'] = project[0].created_at
                image = Image.query.filter_by(id=project[0].image_id).first()
                image_path = utils.get_image_path(image.image_path)
            d['user'] = user
            d['over_introduction'] = False
            if len(company.company_introduction) > 250:
                company.company_introduction = company.company_introduction[:250]
                d['over_introduction'] = True
            d['company'] = company
            d['image_path'] = image_path
            d['user_profile_image_path'] = get_user_profile_image_path(user)
            ret_pros.append(d)

        ret_pros = sorted(ret_pros, key=lambda k: k['last_project_created'], reverse=True)
        return render_template('find_pros.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,ret_pros=ret_pros,pros_size=len(ret_pros),pros_category_name=pros_category_name,findProsForm=findProsForm)


        #return render_template('search_company_test.html',search_company_si=request.form['search_company_si'],search_company_gu=request.form['search_company_gu'],search_company_dong=request.form['search_company_dong'])
        #return render_template('search_company_test.html')

@app.route('/find_pros/<int:pros_category_id>',methods=['GET','POST'])
def find_pros_detail(pros_category_id):

    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
        companySearchForm = CompanySearchForm()
        findProsForm = FindProsForm()

    if request.method == 'GET':
        pros_category_name = Pros_category.query.filter_by(id=pros_category_id).first().category_name
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
            project = Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).all()
            if len(project) == 0:
                d['last_project_created'] = user.created_at
            else :
                d['last_project_created'] = project[0].created_at
                image = Image.query.filter_by(id=project[0].image_id).first()
                image_path = utils.get_image_path(image.image_path)

            d['user'] = user
            d['over_introduction'] = False
            if len(company.company_introduction) > 250:
                company.company_introduction = company.company_introduction[:250]
                d['over_introduction'] = True

            d['company'] = company
            d['image_path'] = image_path
            d['user_profile_image_path'] = get_user_profile_image_path(user)
            ret_pros.append(d)

        ret_pros = sorted(ret_pros, key=lambda k: k['last_project_created'], reverse=True)
        return render_template('find_pros.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,ret_pros=ret_pros,pros_size=len(ret_pros),pros_category_name=pros_category_name,findProsForm=findProsForm,pros_category_id=pros_category_id)
    elif request.method == 'POST':
        pros_category_name = Pros_category.query.filter_by(id=pros_category_id).first().category_name
        ret_pros = []
        if findProsForm.company_gu.data != u'전체':
            if findProsForm.company_dong.data == u'전체':
                companies = Company.query.filter_by(company_si=findProsForm.company_si.data).filter_by(company_gu=findProsForm.company_gu.data).all()
            elif findProsForm.company_dong.data != u'전체':
                companies = Company.query.filter_by(company_si=findProsForm.company_si.data).filter_by(company_gu=findProsForm.company_gu.data).filter_by(company_dong=findProsForm.company_dong.data).all()
        elif findProsForm.company_gu.data == u'전체':
            companies = Company.query.filter_by(company_si=findProsForm.company_si.data).all()

        for company in companies:
            company_has_pros_categories = Company_has_pros_category.query.filter_by(company_id=company.id).all()
            ok = False
            for company_has_pros_category in company_has_pros_categories:
                if company_has_pros_category.pros_category_id == pros_category_id:
                    ok = True
            if not ok:
                continue
            d = {}
            user = User.query.filter_by(id=company.user_id).first()
            project = Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).all()
            image = Image.query.filter_by(id=company.image_id).first()
            image_path = utils.get_image_path(image.image_path)
            if len(project) == 0:
                d['last_project_created'] = user.created_at
            else :
                d['last_project_created'] = project[0].created_at
                image = Image.query.filter_by(id=project[0].image_id).first()
                image_path = utils.get_image_path(image.image_path)
            d['user'] = user
            d['over_introduction'] = False
            if len(company.company_introduction) > 250:
                company.company_introduction = company.company_introduction[:250]
                d['over_introduction'] = True
            d['company'] = company
            d['image_path'] = image_path
            d['user_profile_image_path'] = get_user_profile_image_path(user)
            ret_pros.append(d)

        ret_pros = sorted(ret_pros, key=lambda k: k['last_project_created'], reverse=True)
        return render_template('find_pros.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,ret_pros=ret_pros,pros_size=len(ret_pros),pros_category_name=pros_category_name,findProsForm=findProsForm,pros_category_id=pros_category_id)


@app.route('/photos/',methods=['GET','POST'])
def photos():
    feed_category_id = 0
    feed_category_name = '전체'
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    feed_count = Feed.query.count()
    if request.method == 'GET':
        offset = 15
        projects = Project.query.order_by(Project.created_at.desc())
        ret_feeds = []
        for project in projects:
            project_has_feed = Project_has_feed.query.filter_by(project_id=project.id).first()
            feed = Feed.query.filter_by(id=project_has_feed.feed_id).first()
            d = {}
            image = Image.query.filter_by(id=feed.image_id).first()
            image_path = utils.get_image_path(image.image_path)
            user = User.query.filter_by(id=feed.user_id).first()
            user_profile_image_path = get_user_profile_image_path(user)
            all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()
            all_likes = User_like_feed.query.filter_by(feed_id=feed.id).all()
            is_user_like = False
            if 'user_id' in session:
                if User_like_feed.query.filter_by(user_id=session['user_id']).filter_by(feed_id=feed.id).first():
                    is_user_like = True
            d['number_of_like'] = len(all_likes)
            d['is_user_like'] = is_user_like


            d['image_path'] = image_path
            d['user'] = user
            d['feed'] = feed
            d['number_of_comment'] = len(all_comments)
            d['user_profile_image_path'] = user_profile_image_path 
            ret_feeds.append(d)

        #feeds = Feed.query.order_by(Feed.created_at.desc()).limit(offset).all()
        #ret_feeds = []
        #for feed in feeds:
        #    d = {}
        #    image = Image.query.filter_by(id=feed.image_id).first()
        #    image_path = utils.get_image_path(image.image_path)
        #    user = User.query.filter_by(id=feed.user_id).first()
        #    all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()
        #    d['image_path'] = image_path
        #    d['user'] = user
        #    d['feed'] = feed
        #    d['number_of_comment'] = len(all_comments)
        #    ret_feeds.append(d)

        return render_template('photos.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm, feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id,feed_category_name=feed_category_name, feed_count=feed_count)
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


            all_likes = User_like_feed.query.filter_by(feed_id=feed.id).all()
            is_user_like = False
            if 'user_id' in session:
                if User_like_feed.query.filter_by(user_id=session['user_id']).filter_by(feed_id=feed.id).first():
                    is_user_like = True
            d['number_of_like'] = len(all_likes)
            d['is_user_like'] = is_user_like
            d['image_path'] = image_path
            d['user'] = user
            d['feed'] = feed
            d['number_of_comment'] = len(all_comments)
            ret_feeds.append(d)

        html_code = render_template('photos.html', signupForm=signupForm, signinForm=signinForm,companySignupForm=companySignupForm ,feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id,feed_category_name=feed_category_name,feed_count=feed_count)
        return html_code

@app.route('/photos/<int:feed_category_id>')
def photos_detail(feed_category_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()


    feed_category = Feed_category.query.filter_by(id=feed_category_id).first()
    feed_category_name = feed_category.category_name
    feed_count = Feed.query.filter_by(feed_category_id=feed_category_id).count()
    if request.method == 'GET':
        offset = 15
        projects = Project.query.order_by(Project.created_at.desc())
        ret_feeds = []
        for project in projects:
            project_has_feeds = Project_has_feed.query.filter_by(project_id=project.id).all()
            feed = None
            for project_has_feed in project_has_feeds:
                cur_feed = Feed.query.filter_by(id=project_has_feed.feed_id).first()
                if cur_feed.feed_category_id == feed_category_id:
                    feed = cur_feed
                    break
            if feed == None:
                continue
#            feed = Feed.query.filter_by(id=project_has_feed.feed_id).first()
            d = {}
            image = Image.query.filter_by(id=feed.image_id).first()
            image_path = utils.get_image_path(image.image_path)
            user = User.query.filter_by(id=feed.user_id).first()
            all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()


            all_likes = User_like_feed.query.filter_by(feed_id=feed.id).all()
            is_user_like = False
            if 'user_id' in session:
                if User_like_feed.query.filter_by(user_id=session['user_id']).filter_by(feed_id=feed.id).first():
                    is_user_like = True
            d['number_of_like'] = len(all_likes)
            d['is_user_like'] = is_user_like
            d['image_path'] = image_path
            d['user'] = user
            d['feed'] = feed
            d['number_of_comment'] = len(all_comments)
            ret_feeds.append(d)


        #offset = 10
        #feeds = Feed.query.filter_by(feed_category_id=feed_category_id).order_by(Feed.created_at.desc()).limit(offset).all()
        #ret_feeds = []
        #for feed in feeds:
        #    d = {}
        #    image = Image.query.filter_by(id=feed.image_id).first()
        #    image_path = utils.get_image_path(image.image_path)
        #    user = User.query.filter_by(id=feed.user_id).first()
        #    all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()
        #    d['image_path'] = image_path
        #    d['user'] = user
        #    d['feed'] = feed
        #    d['number_of_comment'] = len(all_comments)
        #    ret_feeds.append(d)

        return render_template('photos.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm, feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id, feed_category_name=feed_category_name, feed_count=feed_count)

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


            all_likes = User_like_feed.query.filter_by(feed_id=feed.id).all()
            is_user_like = False
            if 'user_id' in session:
                if User_like_feed.query.filter_by(user_id=session['user_id']).filter_by(feed_id=feed.id).first():
                    is_user_like = True
            d['number_of_like'] = len(all_likes)
            d['is_user_like'] = is_user_like
            d['image_path'] = image_path
            d['user'] = user
            d['feed'] = feed
            d['number_of_comment'] = len(all_comments)
            ret_feeds.append(d)

        html_code = render_template('photos.html', signupForm=signupForm, signinForm=signinForm,companySignupForm=companySignupForm ,feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id,feed_category_name=feed_category_name,feed_count=feed_count)
        return html_code

@app.route('/photos/grid/',methods=['GET','POST'])
def photos_grid():
    feed_category_id = 0
    feed_category_name = '전체'
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    feed_count = Feed.query.count()
    if request.method == 'GET':
        offset = 15
        projects = Project.query.order_by(Project.created_at.desc())
        ret_feeds = []
        for project in projects:
            project_has_feed = Project_has_feed.query.filter_by(project_id=project.id).first()
            feed = Feed.query.filter_by(id=project_has_feed.feed_id).first()
            d = {}
            image = Image.query.filter_by(id=feed.image_id).first()
            image_path = utils.get_image_path(image.image_path)
            user = User.query.filter_by(id=feed.user_id).first()
            all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()


            all_likes = User_like_feed.query.filter_by(feed_id=feed.id).all()
            is_user_like = False
            if 'user_id' in session:
                if User_like_feed.query.filter_by(user_id=session['user_id']).filter_by(feed_id=feed.id).first():
                    is_user_like = True
            d['number_of_like'] = len(all_likes)
            d['is_user_like'] = is_user_like
            d['image_path'] = image_path
            d['user'] = user
            d['feed'] = feed
            d['number_of_comment'] = len(all_comments)
            ret_feeds.append(d)

        #feeds = Feed.query.order_by(Feed.created_at.desc()).limit(offset).all()
        #ret_feeds = []
        #for feed in feeds:
        #    d = {}
        #    image = Image.query.filter_by(id=feed.image_id).first()
        #    image_path = utils.get_image_path(image.image_path)
        #    user = User.query.filter_by(id=feed.user_id).first()
        #    all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()
        #    d['image_path'] = image_path
        #    d['user'] = user
        #    d['feed'] = feed
        #    d['number_of_comment'] = len(all_comments)
        #    ret_feeds.append(d)

        return render_template('photos_grid.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm, feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id,feed_category_name=feed_category_name, feed_count=feed_count)
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


            all_likes = User_like_feed.query.filter_by(feed_id=feed.id).all()
            is_user_like = False
            if 'user_id' in session:
                if User_like_feed.query.filter_by(user_id=session['user_id']).filter_by(feed_id=feed.id).first():
                    is_user_like = True
            d['number_of_like'] = len(all_likes)
            d['is_user_like'] = is_user_like
            d['image_path'] = image_path
            d['user'] = user
            d['feed'] = feed
            d['number_of_comment'] = len(all_comments)
            ret_feeds.append(d)

        html_code = render_template('photos_grid.html', signupForm=signupForm, signinForm=signinForm,companySignupForm=companySignupForm ,feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id,feed_category_name=feed_category_name,feed_count=feed_count)
        return html_code

@app.route('/photos/<int:feed_category_id>/grid')
def photos_detail_grid(feed_category_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()


    feed_category = Feed_category.query.filter_by(id=feed_category_id).first()
    feed_category_name = feed_category.category_name
    feed_count = Feed.query.filter_by(feed_category_id=feed_category_id).count()
    if request.method == 'GET':
        offset = 15
        projects = Project.query.order_by(Project.created_at.desc())
        ret_feeds = []
        for project in projects:
            project_has_feeds = Project_has_feed.query.filter_by(project_id=project.id).all()
            feed = None
            for project_has_feed in project_has_feeds:
                cur_feed = Feed.query.filter_by(id=project_has_feed.feed_id).first()
                if cur_feed.feed_category_id == feed_category_id:
                    feed = cur_feed
                    break
            if feed == None:
                continue
#            feed = Feed.query.filter_by(id=project_has_feed.feed_id).first()
            d = {}
            image = Image.query.filter_by(id=feed.image_id).first()
            image_path = utils.get_image_path(image.image_path)
            user = User.query.filter_by(id=feed.user_id).first()
            all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()


            all_likes = User_like_feed.query.filter_by(feed_id=feed.id).all()
            is_user_like = False
            if 'user_id' in session:
                if User_like_feed.query.filter_by(user_id=session['user_id']).filter_by(feed_id=feed.id).first():
                    is_user_like = True
            d['number_of_like'] = len(all_likes)
            d['is_user_like'] = is_user_like
            d['image_path'] = image_path
            d['user'] = user
            d['feed'] = feed
            d['number_of_comment'] = len(all_comments)
            ret_feeds.append(d)


        #offset = 10
        #feeds = Feed.query.filter_by(feed_category_id=feed_category_id).order_by(Feed.created_at.desc()).limit(offset).all()
        #ret_feeds = []
        #for feed in feeds:
        #    d = {}
        #    image = Image.query.filter_by(id=feed.image_id).first()
        #    image_path = utils.get_image_path(image.image_path)
        #    user = User.query.filter_by(id=feed.user_id).first()
        #    all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.desc()).all()
        #    d['image_path'] = image_path
        #    d['user'] = user
        #    d['feed'] = feed
        #    d['number_of_comment'] = len(all_comments)
        #    ret_feeds.append(d)

        return render_template('photos_grid.html', signupForm=signupForm, signinForm=signinForm, companySignupForm=companySignupForm, feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id, feed_category_name=feed_category_name, feed_count=feed_count)

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


            all_likes = User_like_feed.query.filter_by(feed_id=feed.id).all()
            is_user_like = False
            if 'user_id' in session:
                if User_like_feed.query.filter_by(user_id=session['user_id']).filter_by(feed_id=feed.id).first():
                    is_user_like = True
            d['number_of_like'] = len(all_likes)
            d['is_user_like'] = is_user_like
            d['image_path'] = image_path
            d['user'] = user
            d['feed'] = feed
            d['number_of_comment'] = len(all_comments)
            ret_feeds.append(d)

        html_code = render_template('photos_grid.html', signupForm=signupForm, signinForm=signinForm,companySignupForm=companySignupForm ,feeds=ret_feeds, offset=offset, feed_category_id=feed_category_id,feed_category_name=feed_category_name,feed_count=feed_count)
        return html_code


@app.route('/shop/',methods=['GET','POST'])
def shop():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    cur_category_product_count = Product.query.count()
    t_products = Product.query.order_by(Product.created_at.desc()).all()
    products = []
    for t_product in t_products:
        product_has_image = Product_has_image.query.filter_by(product_id=t_product.id).first()
        image_id = product_has_image.image_id
        image = Image.query.filter_by(id=image_id).first()
        image_path = utils.get_image_path(image.image_path)
        user = User.query.filter_by(id=t_product.user_id).first()
        d = {
            'product': t_product,
            'product_real_price': utils.convert_price_to_won(t_product.product_price),
            'product_real_sale_price': utils.convert_price_to_won(t_product.product_sale_price),
            'user': user,
            'image_path': image_path
        }
        products.append(d)

    ret_category = utils.get_all_category()
    ret = {
        'cur_category_product_count': cur_category_product_count,
        'shop_category_id': 0,
        'shop_category_name': '전체',
        'category': ret_category,
        'products': products
    }

    return render_template('shop.html', signupForm=signupForm, signinForm=signinForm,companySignupForm=companySignupForm,ret=ret)

@app.route('/shop/<int:shop_category_id>')
def shop_detail(shop_category_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    products = []
    cur_category_product_count = 0
    shop_category_1st_list = utils.get_shop_category_1st_list()
    if shop_category_id in shop_category_1st_list:
        for i in xrange(len(shop_category_1st_list)):
            if shop_category_id == shop_category_1st_list[i]:
                idx = i
                break
        shop_category_2nd_list = utils.get_shop_category_tree()[idx]
        for cur_shop_category_id in shop_category_2nd_list:
            cur_category_product_count += Product.query.filter_by(shop_category_id=cur_shop_category_id).count()
            t_products = Product.query.filter_by(shop_category_id=cur_shop_category_id).order_by(Product.created_at.desc()).all()
            for t_product in t_products:
                product_has_image = Product_has_image.query.filter_by(product_id=t_product.id).first()
                image_id = product_has_image.image_id
                image = Image.query.filter_by(id=image_id).first()
                image_path = utils.get_image_path(image.image_path)
                user = User.query.filter_by(id=t_product.user_id).first()
                d = {
                    'product': t_product,
                    'product_real_price': utils.convert_price_to_won(t_product.product_price),
                    'product_real_sale_price': utils.convert_price_to_won(t_product.product_sale_price),
                    'user': user,
                    'image_path': image_path
                }
                products.append(d)
    else:
        cur_category_product_count = Product.query.filter_by(shop_category_id=shop_category_id).count()
        t_products = Product.query.filter_by(shop_category_id=shop_category_id).order_by(Product.created_at.desc()).all()
        for t_product in t_products:
            product_has_image = Product_has_image.query.filter_by(product_id=t_product.id).first()
            image_id = product_has_image.image_id
            image = Image.query.filter_by(id=image_id).first()
            image_path = utils.get_image_path(image.image_path)
            user = User.query.filter_by(id=t_product.user_id).first()
            d = {
                'product': t_product,
                'product_real_price': utils.convert_price_to_won(t_product.product_price),
                'product_real_sale_price': utils.convert_price_to_won(t_product.product_sale_price),
                'user': user,
                'image_path': image_path
            }
            products.append(d)

    ret_category = utils.get_all_category()
    ret = {
        'cur_category_product_count': cur_category_product_count,
        'shop_category_id': shop_category_id,
        'shop_category_name': utils.get_shop_category_dictionary()[shop_category_id],
        'category': ret_category,
        'products': products
    }

    return render_template('shop.html', signupForm=signupForm, signinForm=signinForm,companySignupForm=companySignupForm,ret=ret )

@app.route('/test')
def test():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    return render_template('test.html',signinForm=signinForm,signupForm=signupForm,companySignupForm=companySignupForm)

@app.route('/test_like')
def test_like():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()

    return render_template('test_like.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm)

@app.route('/like_post',methods=['POST'])
def like_post():
    is_liked = False
    user_id = request.form['user_id']
    feed_id = request.form['feed_id']
    user_like_feed = User_like_feed.query.filter_by(user_id=user_id).filter_by(feed_id=feed_id).first()
    if user_like_feed:
        is_liked = True
        db.session.delete(user_like_feed)
        db.session.commit()
    else :
        is_liked = False
        user = User.query.filter_by(id=user_id).first()
        feed = Feed.query.filter_by(id=feed_id).first()
        user_like_feed = User_like_feed(user.id,feed.id)
        user_like_feed.feed_id = feed_id
        user_like_feed.user_id = user_id
        db.session.add(user_like_feed)
        db.session.commit()

    return json.dumps({'status':'OK','user_id':request.form['user_id'],'feed_id':request.form['feed_id'],'is_liked':is_liked,'number_of_like':User_like_feed.query.filter_by(feed_id=feed_id).count()})

@app.route('/follow_post',methods=['POST'])
def follow_post():
    is_followed = False
    from_user_id = request.form['from_user_id']
    to_user_id = request.form['to_user_id']
    follow = Follow.query.filter_by(from_user_id=from_user_id).filter_by(to_user_id=to_user_id).first()
    if follow:
        is_followed = True
        db.session.delete(follow)
        db.session.commit()
    else:
        is_followed = False
        from_user = User.query.filter_by(id=from_user_id).first()
        to_user = User.query.filter_by(id=to_user_id).first()
        follow = Follow(from_user.id,to_user.id)
        db.session.add(follow)
        db.session.commit()
    return json.dumps({'status':'OK','from_user_id':from_user_id,'to_user_id':to_user_id,'is_followed':is_followed,'number_of_from_user_follow':Follow.query.filter_by(from_user_id=from_user_id).count(),'number_of_to_user_follow':Follow.query.filter_by(to_user_id=to_user_id).count()})

@app.route('/json/address')
def address():
    with open('/home/howsmart/howsmart/app/address.json','r') as fp:
        r = json.loads(fp.read())
    return jsonify(results=r)

@app.route('/add_tag',methods=['POST'])
def add_tag():
    d = {
        'status': 'OK',
        'tag_x': request.form['tag_x'],
        'tag_y': request.form['tag_y'],
        'feed_id': request.form['feed_id'],
        'tag_name': request.form['tag_name'],
        'tag_link': request.form['tag_link']
            }
    if len(d['tag_name']) == 0 or len(d['tag_link']) == 0:
        return json.dumps({'error': 'tag-name or tag-link is none'}), 500
    tag = Tag(d['tag_x'],d['tag_y'],d['feed_id'],d['tag_name'],d['tag_link'])
    db.session.add(tag)
    db.session.commit()
    return json.dumps(d)

@app.route('/project_detail_edit_done',methods=['POST'])
def project_detail_edit_done():
    feed_size = int(request.form['feed_size'])
    t_ids = []
    t_original_ids = []
    for i in xrange(feed_size):
        t_ids.append(request.form['ids['+str(i)+']'])
        t_original_ids.append(request.form['original_ids['+str(i)+']'])
    d = {
        'status': 'OK',
        'ids': t_ids,
        'original_ids': t_original_ids,
        'project_name': request.form['project_name'],
        'project_body': request.form['project_body'],
        'project_id': request.form['project_id']
    }
    print d
    project = Project.query.filter_by(id=int(d['project_id'])).first()
    project.project_name = d['project_name']
    project.project_body = d['project_body']
    db.session.commit()
    is_changed = set()
    for i in xrange(len(d['ids'])):
        f1 = Feed.query.filter_by(id=int(d['original_ids'][i].split('-')[-1])).first()
        f2 = Feed.query.filter_by(id=int(d['ids'][i].split('-')[-1])).first()
        if f1.id in is_changed or f2.id in is_changed:
            continue
        print is_changed
        is_changed.add(f1.id)
        print f1.id, f2.id

        t_title = f1.title
        t_body = f1.body
        t_image_id = f1.image_id
        t_feed_category_id = f1.feed_category_id
        t_status_id = f1.status_id
        print f1.image_id,f2.image_id

        f1.title = f2.title
        f1.body = f2.body
        f1.image_id = f2.image_id
        f1.feed_category_id = f2.feed_category_id
        f1.status_id = f2.status_id

        f2.title = t_title
        f2.body = t_body
        f2.image_id = t_image_id
        f2.feed_category_id = t_feed_category_id
        f2.status_id = t_status_id
        print f1.image_id,f2.image_id
    db.session.commit()
    project.image_id = Feed.query.filter_by(id=Project_has_feed.query.filter_by(project_id=project.id).first().feed_id).first().image_id
    db.session.commit()
    return json.dumps(d)


@app.route('/company_portfolio_edit_done',methods=['POST'])
def company_portfolio_edit_done():
    d = {
        'status': 'OK',
        'company_introduction': request.form['company_introduction'],
        'company_tel': request.form['company_tel'],
        'company_website': request.form['company_website'],
        'company_id': request.form['company_id']
            }
    company = Company.query.filter_by(id=int(d['company_id'])).first()
    company.company_introduction = d['company_introduction']
    company.company_tel = d['company_tel']
    company.company_website = d['company_website']
#    db.session.commit()
    return json.dumps(d)

@app.route('/create_post',methods=['GET','POST'])
def create_post():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    if request.method == 'POST':
        file = request.files['imgup']
        filename = secure_filename(file.filename)
        if utils.allowedFile(filename):
            directory_url = os.path.join(app.config['UPLOAD_FOLDER'],session['email'])
            utils.createDirectory(directory_url)
            file_path = os.path.join(directory_url,filename)
            file.save(file_path)
            image = Image(file_path)
            image.user_id = session['user_id']
            image.created_at = datetime.utcnow()
            db.session.add(image)
            db.session.commit()
        blog_post = Blog_post(request.form['post-name'],request.form['post-body'],request.form['post-summary'],datetime.utcnow(),image.id,session['user_id'])
        db.session.add(blog_post)
        db.session.commit()
        return redirect(url_for('create_post'))
    return render_template('create_post.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm)

@app.route('/post_image_save',methods=['POST'])
def post_image_save():
    file = request.files['file']
    filename = secure_filename(file.filename)
    if utils.allowedFile(filename):
        directory_url = os.path.join(app.config['UPLOAD_FOLDER'],session['email'])
        utils.createDirectory(directory_url)
        file_path = os.path.join(directory_url,filename)
        file.save(file_path)
        image = Image(file_path)
        image.user_id = session['user_id']
        image.created_at = datetime.utcnow()
        db.session.add(image)
        db.session.commit()
    else:
        return json.dumps({'status':'error','message':'extention error'})
    print file.filename
    print file_path
    d = {
        'status': 'OK',
        'url': utils.get_image_path(image.image_path)
            }
    return json.dumps(d)

@app.route('/blog_post/<post_id>',methods=['GET','POST'])
def blog_post(post_id):
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
        commentForm = CommentForm()
    blog_post = Blog_post.query.filter_by(id=post_id).first()
    user = User.query.filter_by(id=blog_post.user_id).first()
    blog_post_comments = Blog_post_comment.query.filter_by(blog_post_id=blog_post.id).order_by(Blog_post_comment.created_at.asc()).all()

    comments_dict_list = []
    for all_comment in blog_post_comments:
        comment_user = User.query.filter_by(id=all_comment.user_id).first()
        cur = {
                'comment': all_comment,
                'user': comment_user,
                'user_profile_image_path': get_user_profile_image_path(comment_user)
                }
        comments_dict_list.append(cur)

    d = {
            'post': blog_post,
            'user': user,
            'all_comments':comments_dict_list 
            }

    if request.method == 'GET':
        return render_template('blog_post.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,post=d,commentForm=commentForm)
    elif request.method == 'POST':
        if not commentForm.validate():
            return render_template('blog_post.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm,post=d,commentForm=commentForm)
        if commentForm.validate_on_submit():
            blog_post_comment = Blog_post_comment(commentForm.body.data, datetime.utcnow(), post_id, session['user_id'], 1)
            db.session.add(blog_post_comment)
            db.session.commit()
            d['all_comments'] = Blog_post_comment.query.filter_by(blog_post_id=post_id).order_by(Blog_post_comment.created_at.asc()).all()
        return redirect(url_for('blog_post',post_id=post_id))

@app.route('/save_post',methods=['POST'])
def save_post():
    d = {
            'status':'OK',
            'post_id': int(request.form['post_id']),
            'user_id': int(request.form['user_id']),
            'comment': request.form['comment']
            }
    user_save_post = User_save_post.query.filter_by(user_id=d['user_id']).filter_by(post_id=d['post_id']).first()
    if user_save_post:
        return json.dumps({'status':'error','message':'is aleady save'})
    user_save_post = User_save_post(d['user_id'],d['post_id'],d['comment'])
    db.session.add(user_save_post)
    db.session.commit()
    return json.dumps(d)

@app.route('/save_feed',methods=['POST'])
def save_feed():
    d = {
        'status': 'OK',
        'feed_id': int(request.form['feed_id']),
        'user_id': int(request.form['user_id']),
        'comment': request.form['comment']
            }
    user_save_feed = User_save_feed.query.filter_by(user_id=d['user_id']).filter_by(feed_id=d['feed_id']).first()
    if user_save_feed:
        return json.dumps({'status':'error','message':'is aleady save'})
    user_save_feed = User_save_feed(d['user_id'],d['feed_id'],d['comment'])
    db.session.add(user_save_feed)
    db.session.commit()
    return json.dumps(d)

@app.route('/save_product',methods=['POST'])
def save_product():
    d = {
            'status':'OK',
            'product_id' : int(request.form['product_id']),
            'user_id': int(request.form['user_id']),
            'comment': request.form['comment']
            }
    user_save_product = User_save_product.query.filter_by(user_id=d['user_id']).filter_by(product_id=d['product_id']).first()
    if user_save_product:
        return json.dumps({'status':'error','message':'is aleady save'})
    user_save_product = User_save_product(d['user_id'],d['product_id'],d['comment'])
    db.session.add(user_save_product)
    db.session.commit()
    json.dumps(d)

@app.route('/image_crop',methods=['GET','POST'])
def image_crop():
    with app.app_context():
        signupForm = SignupForm()
        signinForm = SigninForm()
        companySignupForm = CompanySignupForm()
    return render_template('image_crop.html',signupForm=signupForm,signinForm=signinForm,companySignupForm=companySignupForm)

@app.route('/image_crop_upload',methods=['POST'])
def image_crop_upload():
    base64_string = request.form['imageData']
    filename = "uploaded_image%s.png" % str(time.time()).replace('.','_')
    directory_url = os.path.join(app.config['UPLOAD_FOLDER'],session['email'])
    utils.createDirectory(directory_url)
    directory_url = os.path.join(directory_url,'profile')
    utils.createDirectory(directory_url)
    file_path = os.path.join(directory_url,filename)
    fp = open(file_path,'wb')
    fp.write(base64_string.decode('base64'))
    fp.close()

    user = User.query.filter_by(id=session['user_id']).first()
    image = Image(file_path)
    image.user_id = user.id 
    image.created_at = datetime.utcnow()
    db.session.add(image)
    db.session.commit()

    user_profile = User_profile(user.id, image.id, datetime.utcnow())
    db.session.add(user_profile)
    db.session.commit()

    d = {
        'status': 'OK',
            }
    return json.dumps(d)
