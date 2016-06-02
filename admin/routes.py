# -*- coding:utf-8 -*-
from flask import Flask, url_for
from flask.ext.paginate import Pagination
from werkzeug import secure_filename
import utils
import os
import time
from sqlalchemy import *

from config import UPLOAD_FOLDER, HOWSMART_DATABASE_URI, HOWSMART_SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']   = HOWSMART_DATABASE_URI
app.config['SECRET_KEY']                = HOWSMART_SECRET_KEY
app.config['UPLOAD_FOLDER']             = UPLOAD_FOLDER

from models import (
        db,
        User,
        Feed,
        Image,
        Comment,
        Company,
        Project,
        Project_has_feed,
        Pros_category,
        Company_has_pros_category,
        Feed_category, Product,
        Product_has_image,
        Shop_category,
        User_like_feed,
        Follow, Status,
        Tag,
        Project_type_category,
        Style_category,
        Project_hash_tag,
        Product_hash_tag,
        Blog_post,
        Blog_post_comment,
        User_save_feed,
        User_save_post,
        User_save_product,
        User_profile,
        Review,
        Qna_q,
        Qna_a,
        )

db.init_app(app)

import json
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask import get_flashed_messages
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
from forms import SigninForm, WriteFeedForm, CommentForm, MakeProjectForm, CreateProjectForm, ProjectEditForm, CreateProductForm, CompanySearchForm, FindProsForm
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def get_feed_information(feeds):
    ret = []
    for feed in feeds:
        d = {}
        image = Image.query.filter_by(id=feed.image_id).first()
        image_path = utils.get_image_path(image.image_path)
        user = User.query.filter_by(id=feed.user_id).first()
        all_comments = Comment.query.filter_by(feed_id=feed.id).order_by(Comment.created_at.asc()).all()
        status_name = Status.query.filter_by(id=feed.status_id).first().status_name

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
        d['status_name'] = status_name
        ret.append(d)
    return ret

def get_pros_information(users):
    ret = []
    for user in users:
        d = {}
        company = Company.query.filter_by(user_id=user.id).first()
        project = Project.query.filter_by(company_id=company.id).order_by(Project.created_at.desc()).all()
        image = Image.query.filter_by(id=company.image_id).first()
        image_path = utils.get_image_path(image.image_path)
        status_name = Status.query.filter_by(id=user.status_id).first().status_name
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
        d['status_name'] = status_name
        ret.append(d)
    return ret

def get_shop_information(t_products):
    products = []
    for t_product in t_products:
        product_has_image = Product_has_image.query.filter_by(product_id=t_product.id).first()
        image_id = product_has_image.image_id
        image = Image.query.filter_by(id=image_id).first()
        image_path = utils.get_image_path(image.image_path)
        user = User.query.filter_by(id=t_product.user_id).first()
        category_name = Shop_category.query.filter_by(id=t_product.shop_category_id).first().category_name
        status_name = Status.query.filter_by(id=t_product.status_id).first().status_name
        d = {
            'product': t_product,
            'product_real_price': utils.convert_price_to_won(t_product.product_price),
            'user': user,
            'image_path': image_path,
            'category_name': category_name,
            'status_name': status_name
        }
        products.append(d)
    return products

def get_company_information(users):
    ret = []
    for user in users:
        company = Company.query.filter_by(user_id=user.id).first()
        project = Project.query.filter_by(company_id=company.id).all()
        product = Product.query.filter_by(user_id=user.id).all()
        status_name = Status.query.filter_by(id=user.status_id).first().status_name
        d = {
                'user': user,
                'company': company,
                'project': project,
                'product': product,
                'status_name': status_name
                }
        ret.append(d)
    return ret

def get_comment_information(comments):
    ret = []
    for comment in comments:
        user = User.query.filter_by(id=comment.user_id).first()
        feed = Feed.query.filter_by(id=comment.feed_id).first()
        status_name = Status.query.filter_by(id=comment.status_id).first().status_name
        d = {
                'comment': comment,
                'user': user,
                'feed': feed,
                'status_name': status_name
                }
        ret.append(d)
    return ret

def get_user_information(users):
    ret = []
    for user in users:
        status_name = Status.query.filter_by(id=user.status_id).first().status_name
        d = {
                'user': user,
                'status_name': status_name
                }
        ret.append(d)
    return ret

def get_project_information(projects):
    ret = []
    for project in projects:
        company = Company.query.filter_by(id=project.company_id).first()
        user = User.query.filter_by(id=company.user_id).first()
        status_name = Status.query.filter_by(id=project.status_id).first().status_name
        project_has_feeds = Project_has_feed.query.filter_by(project_id=project.id).all()
        d = {
                'company': company,
                'project': project,
                'user': user,
                'status_name' : status_name,
                'project_has_feeds' : project_has_feeds
                }
        ret.append(d)
    return ret

def get_qna_q_information(qna_qs):
    ret = []
    for qna_q in qna_qs:
        company = Company.query.filter_by(id=qna_q.company_id).first()
        company_user = User.query.filter_by(id=company.user_id).first()
        user = User.query.filter_by(id=qna_q.user_id).first()
        d = {
                'company_user': company_user,
                'qna_q': qna_q,
                'company': company,
                'user': user
                }
        ret.append(d)
    return ret

def get_qna_a_information(qna_as):
    ret = []
    for qna_a in qna_as:
        qna_q = Qna_q.query.filter_by(id=qna_a.qna_q_id).first()
        user = User.query.filter_by(id=qna_a.user_id).first()
        d = {
            'qna_a': qna_a,
            'qna_q': qna_q,
            'user': user
                }
        ret.append(d)
    return ret


@app.route('/',methods=['GET','POST'])
def main():
    if not 'logged_in' in session:
        return redirect(url_for('login'))
    if session['level'] != 99:
        return redirect(url_for('signout'))
    return render_template('dashboard.html') 

@app.route('/login',methods=['GET','POST'])
def login():
    with app.app_context():
        signinForm = SigninForm()
    if request.method == 'POST':
        if not signinForm.validate():
            return render_template('login.html',signinForm=signinForm)
        else:
            user = User.query.filter_by(email=signinForm.email.data.lower()).first()
            session['email'] = signinForm.email.data
            session['username'] = user.username
            session['logged_in'] = True
            session['user_id'] = user.id
            session['level'] = user.level
            if user.level == 1:
                session['is_company'] = False
            elif user.level == 2:
                session['is_company'] = True

            return redirect(url_for('main'))
    elif request.method == 'GET':
        return render_template('login.html',signinForm=signinForm)

@app.route('/logout')
def signout():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    session.pop('email', None)
    session.pop('username', None)
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('is_company',None)
    session.pop('level',None)
    return redirect(url_for('login'))

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/photos')
def photos():
    search = False
    per_page = 20
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    total_count = Feed.query.count()
    feeds = Feed.query.order_by(Feed.created_at.desc()).limit(per_page).offset((page-1)*per_page)
    feeds = get_feed_information(feeds)
    pagination = Pagination(page=page, total=total_count, search=search, record_name='feed', per_page=per_page)
    return render_template('photos.html',feeds=feeds, pagination=pagination)

@app.route('/project')
def project():
    search = False
    per_page = 20
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    total_count = Project.query.count()
    projects = Project.query.order_by(Project.created_at.desc()).limit(per_page).offset((page-1)*per_page)
    projects = get_project_information(projects)
    pagination = Pagination(page=page, total=total_count, search=search, record_name='project', per_page=per_page)

    return render_template('project.html',projects=projects, pagination=pagination)

@app.route('/pros')
def pros():
    search = False
    per_page = 20
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    total_count = User.query.filter_by(level=2).count()
    pros = User.query.filter_by(level=2).order_by(User.created_at.desc()).limit(per_page).offset((page-1)*per_page)
    pros = get_pros_information(pros)
    pagination = Pagination(page=page, total=total_count, search=search, record_name='company', per_page=per_page)
    return render_template('pros.html',pros=pros, pagination=pagination)

@app.route('/shop')
def shop():
    search = False
    per_page = 20
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    total_count = Product.query.count()
    products = Product.query.order_by(Product.created_at.desc()).limit(per_page).offset((page-1)*per_page)
    products = get_shop_information(products)
    pagination = Pagination(page=page, total=total_count, search=search, record_name='product', per_page=per_page)

    return render_template('shop.html',products=products, pagination=pagination)

@app.route('/qna_q')
def qna_q():
    search = False
    per_page = 20
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    total_count = Qna_q.query.count()
    qna_qs = Qna_q.query.order_by(Qna_q.created_at.desc()).limit(per_page).offset((page-1)*per_page)
    qna_qs = get_qna_q_information(qna_qs)
    pagination = Pagination(page=page, total=total_count, search=search, record_name='qna_q', per_page=per_page)
    return render_template('qna_q.html',qna_qs=qna_qs,pagination=pagination)

@app.route('/qna_a')
def qna_a():
    search = False
    per_page = 20
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    total_count = Qna_a.query.count()
    qna_as = Qna_a.query.order_by(Qna_a.created_at.desc()).limit(per_page).offset((page-1)*per_page)
    qna_as = get_qna_a_information(qna_as)
    pagination = Pagination(page=page, total=total_count, search=search, record_name='qna_a', per_page=per_page)
    return render_template('qna_a.html',qna_as=qna_as,pagination=pagination)

@app.route('/user_management')
def user_management():
    users = User.query.filter_by(level=1).order_by(User.created_at.desc()).all()
    users = get_user_information(users)
    return render_template('user_management.html',users=users)

@app.route('/company_management')
def company_management():
    users = User.query.filter_by(level=2).order_by(User.created_at.desc()).all()
    companies = get_company_information(users)
    return render_template('company_management.html',companies=companies)

@app.route('/accept_new_project')
def accept_new_project():
    projects = Project.query.filter_by(status_id=2).order_by(Project.created_at.asc()).all()
    projects = get_project_information(projects)
    return render_template('accept_new_project.html',projects=projects)

@app.route('/accept_modified_project')
def accept_modified_project():
    projects = Project.query.filter_by(status_id=2).order_by(Project.created_at.asc()).all()
    projects = get_project_information(projects)
    return render_template('accept_modified_project.html',projects=projects)

@app.route('/accept_new_product')
def accept_new_product():
    products = Product.query.filter_by(status_id=2).order_by(Product.created_at.desc()).all()
    products = get_shop_information(products)
    return render_template('accept_new_product.html',products=products)

@app.route('/accept_modified_product')
def accept_modified_product():
    products = Product.query.filter_by(status_id=2).order_by(Product.created_at.desc()).all()
    products = get_shop_information(products)
    return render_template('accept_modified_product.html',products=products)

@app.route('/accepted_project')
def accepted_project():
    projects = Project.query.filter_by(status_id=1).order_by(Project.created_at.desc()).all()
    projects = get_project_information(projects)
    return render_template('accepted_project.html',projects=projects)

@app.route('/accepted_product')
def accepted_product():
    products = Product.query.filter_by(status_id=1).order_by(Product.created_at.desc()).all()
    products = get_shop_information(products)
    return render_template('accepted_product.html',products=products)

@app.route('/comment')
def comment():
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    comments = get_comment_information(comments)
    return render_template('comment.html',comments=comments)

@app.route('/photos_edit',methods=['POST'])
def photos_edit():
    if request.form['action'] == 'delete':
        feed = Feed.query.filter_by(id=int(request.form['id'])).first()
        project_has_feeds = Project_has_feed.query.filter_by(feed_id=feed.id).all()
        project = None
        if len(project_has_feeds) != 0 :
            project = Project.query.filter_by(id=project_has_feeds[0].project_id).first()
        for project_has_feed in project_has_feeds:
            db.session.delete(project_has_feed)
        if project:
            project_has_feeds = Project_has_feed.query.filter_by(project_id=project.id).all()
            if len(project_has_feeds) == 0:
                project_hash_tags = Project_hash_tag.query.filter_by(project_id=project.id).all()
                for project_hash_tag in project_hash_tags:
                    db.session.delete(project_hash_tag)
                db.session.commit()
                db.session.delete(project)
                db.session.commit()
        comments = Comment.query.filter_by(feed_id=feed.id).all()
        for comment in comments:
            db.session.delete(comment)
        tags = Tag.query.filter_by(feed_id=feed.id).all()
        for tag in tags:
            db.session.delete(tag)
        user_save_feeds = User_save_feed.query.filter_by(feed_id=feed.id).all()
        for user_save_feed in user_save_feeds:
            db.session.delete(user_save_feed)
        user_like_feeds = User_like_feed.query.filter_by(feed_id=feed.id).all()
        for user_like_feed in user_like_feeds:
            db.session.delete(user_like_feed)
        db.session.commit()
        db.session.delete(feed)
        db.session.commit()
        print 'ok'
    elif request.form['action'] == 'edit':
        feed = Feed.query.filter_by(id=int(request.form['id'])).first()
        feed.title = request.form['title'].strip()
        feed.body = request.form['body'].strip()
        feed.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('photos'))

@app.route('/project_edit',methods=['POST'])
def project_edit():
    if request.form['action'] == 'delete':
        project = Project.query.filter_by(id=int(request.form['id'])).first()
        project_has_feeds = Project_has_feed.query.filter_by(project_id=project.id).all()
        for project_has_feed in project_has_feeds:
            feed = Feed.query.filter_by(id=project_has_feed.feed_id).first()
            comments = Comment.query.filter_by(feed_id=feed.id).all()
            for comment in comments:
                db.session.delete(comment)
            tags = Tag.query.filter_by(feed_id=feed.id).all()
            for tag in tags:
                db.session.delete(tag)
            user_save_feeds = User_save_feed.query.filter_by(feed_id=feed.id).all()
            for user_save_feed in user_save_feeds:
                db.session.delete(user_save_feed)
            user_like_feeds = User_like_feed.query.filter_by(feed_id=feed.id).all()
            for user_like_feed in user_like_feeds:
                db.session.delete(user_like_feed)
            db.session.delete(project_has_feed)
            db.session.commit()
            db.session.delete(feed)
            db.session.commit()
        project_hash_tags = Project_hash_tag.query.filter_by(project_id=project.id).all()
        for project_hash_tag in project_hash_tags:
            db.session.delete(project_hash_tag)
        db.session.commit()
        db.session.delete(project)
        db.session.commit()

    elif request.form['action'] == 'edit':
        project = Project.query.filter_by(id=int(request.form['id'])).first()
        project.project_name = request.form['name'].strip()
        project.project_body = request.form['body'].strip()
        db.session.commit()
    return redirect(url_for('project'))

@app.route('/pros_edit',methods=['POST'])
def pros_edit():
    if request.form['action'] == 'delete':
        company = Company.query.filter_by(id=int(request.form['id'])).first()
        user = User.query.filter_by(id=company.user_id).first()
        blog_posts = Blog_post.query.filter_by(user_id=user.id).all()
        for blog_post in blog_posts:
            blog_post_comments = Blog_post_comment.query.filter_by(blog_post_id=blog_post.id).all()
            for blog_post_comment in blog_post_comments:
                db.session.delete(blog_post_comment)
            db.session.delete(blog_post)
        blog_post_comments = Blog_post_comment.query.filter_by(user_id=user.id).all()
        for blog_post_comment in blog_post_comments:
            db.session.delete(blog_post_comment)
        comments = Comment.query.filter_by(user_id=user.id).all()
        for comment in comments:
            db.session.delete(comment)
        company_has_pros_categorys = Company_has_pros_category.query.filter_by(company_id=company.id).all()
        for company_has_pros_category in company_has_pros_categorys:
            db.session.delete(company_has_pros_category)
        projects = Project.query.filter_by(company_id=company.id).all()
        for project in projects:
            project = Project.query.filter_by(id=int(request.form['id'])).first()
            project_has_feeds = Project_has_feed.query.filter_by(project_id=project.id).all()
            for project_has_feed in project_has_feeds:
                feed = Feed.query.filter_by(id=project_has_feed.feed_id).first()
                comments = Comment.query.filter_by(feed_id=feed.id).all()
                for comment in comments:
                    db.session.delete(comment)
                tags = Tag.query.filter_by(feed_id=feed.id).all()
                for tag in tags:
                    db.session.delete(tag)
                user_save_feeds = User_save_feed.query.filter_by(feed_id=feed.id).all()
                for user_save_feed in user_save_feeds:
                    db.session.delete(user_save_feed)
                user_like_feeds = User_like_feed.query.filter_by(feed_id=feed.id).all()
                for user_like_feed in user_like_feeds:
                    db.session.delete(user_like_feed)
                db.session.delete(project_has_feed)
                db.session.delete(feed)
            project_hash_tags = Project_hash_tag.query.filter_by(project_id=project.id).all()
            for project_hash_tag in project_hash_tags:
                db.session.delete(project_hash_tag)
            db.session.commit()
            db.session.delete(project)
            db.session.commit()
        follows = Follow.query.filter(or_(Follow.from_user_id==user.id,Follow.to_user_id==user.id))
        for follow in follows:
            db.session.delete(follow)
        products = Product.query.filter_by(user_id=user.id).all()
        for product in products:
            product_has_images = Product_has_image.query.filter_by(product_id=product.id).all()
            for product_has_image in product_has_images:
                db.session.delete(product_has_image)
            product_hash_tags = Product_hash_tag.query.filter_by(product_id=product.id).all()
            for product_hash_tag in product_hash_tags:
                db.session.delete(product_hash_tag)
            db.session.commit()
            db.session.delete(product)
            db.session.commit()
        qna_qs = Qna_q.query.filter_by(user_id=user.id).all()
        for qna_q in qna_qs:
            db.session.delete(qna_q)
        qna_as = Qna_a.query.filter_by(user_id=user.id).all()
        for qna_a in qna_as:
            db.session.delete(qna_a)
        reviews = Review.query.filter(or_(Review.user_id==user.id,Review.company_id==company.id))
        for review in reviews:
            db.session.delete(review)
        user_like_feeds = User_like_feed.query.filter_by(user_id=user.id).all()
        for user_like_feed in user_like_feeds:
            db.session.delete(user_like_feed)
        user_profiles = User_profile.query.filter_by(user_id=user.id).all()
        for user_profile in user_profiles:
            db.session.delete(user_profile)
        user_save_feeds = User_save_feed.query.filter_by(user_id=user.id).all()
        for user_save_feed in user_save_feeds:
            db.session.delete(user_save_feed)
        user_save_posts = User_save_post.query.filter_by(user_id=user.id).all()
        for user_save_post in user_save_posts:
            db.session.delete(user_save_post)
        user_save_products = User_save_product.query.filter_by(user_id=user.id).all()
        for user_save_product in user_save_products:
            db.session.delete(user_save_product)
        db.session.commit()
        db.session.delete(company)
        db.session.commit()
        images = Image.query.filter_by(user_id=user.id).all()
        for image in images:
            db.session.delete(image)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()

    elif request.form['action'] == 'edit':
        company = Company.query.filter_by(id=int(request.form['id'])).first()
        company.company_introduction = request.form['introduction'].strip()
        company.company_tel = request.form['tel'].strip()
        company.company_website = request.form['website'].strip()
        company.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('pros'))

@app.route('/shop_edit',methods=['POST'])
def shop_edit():
    if request.form['action'] == 'delete':
        product = Product.query.filter_by(id=int(request.form['id'])).first()
        product_has_images = Product_has_image.query.filter_by(product_id=product.id).all()
        for product_has_image in product_has_images:
            db.session.delete(product_has_image)
        product_hash_tags = Product_hash_tag.query.filter_by(product_id=product.id).all()
        for product_hash_tag in product_hash_tags:
            db.session.delete(product_hash_tag)
        db.session.commit()
        db.session.delete(product)
        db.session.commit()
    elif request.form['action'] == 'edit':
        product = Product.query.filter_by(id=int(request.form['id'])).first()
        product.product_name = request.form['product_name'].strip()
        product.product_desc = request.form['product_desc'].strip()
        product.product_price = request.form['product_price'].strip()
        product.product_color = request.form['product_color'].strip()
        product.product_size = request.form['product_size'].strip()
        product.product_model_name = request.form['product_model_name'].strip()
        product.product_meterial = request.form['product_meterial'].strip()
        product.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('shop'))

@app.route('/user_management_edit',methods=['POST'])
def user_management_edit():
    if request.form['action'] == 'delete':
        print 'delete'
    elif request.form['action'] == 'edit':
        user = User.query.filter_by(id=int(request.form['id'])).first()
        user.username = request.form['username'].strip()
        user.level = int(request.form['level'])
        user.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('user_management'))

@app.route('/company_management_edit',methods=['POST'])
def company_management_edit():
    if request.form['action'] == 'delete':
        print 'delete'
    elif request.form['action'] == 'edit':
        company = Company.query.filter_by(id=int(request.form['id'])).first()
        user = User.query.filter_by(id=company.user_id).first()
        user.username = request.form['username'].strip()
        company.company_introduction = request.form['introduction'].strip()
        company.company_tel = request.form['tel'].strip()
        company.company_website = request.form['website'].strip()
        user.level = int(request.form['level'])
        company.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('company_management'))

@app.route('/qna_a_edit',methods=['POST'])
def qna_a_edit():
    if request.form['action'] == 'delete':
        qna_a = Qna_a.query.filter_by(id=int(request.form['id'])).first()
        db.session.delete(qna_a)
        db.session.commit()
    elif request.form['action'] == 'edit':
        qna_a = Qna_a.query.filter_by(id=int(request.form['id'])).first()
    return redirect(url_for('qna_a'))


@app.route('/qna_q_edit',methods=['POST'])
def qna_q_edit():
    if request.form['action'] == 'delete':
        qna_q = Qna_q.query.filter_by(id=int(request.form['id'])).first()
        qna_as = Qna_a.query.filter_by(qna_q_id=qna_q.id).all()
        for qna_a in qna_as:
            db.session.delete(qna_a)
        db.session.commit()
        db.session.delete(qna_q)
        db.session.commit()
    elif request.form['action'] == 'edit':
        qna_q = Qna_q.query.filter_by(id=int(request.form['id'])).first()
    return redirect(url_for('qna_q'))

@app.route('/comment_edit',methods=['POST'])
def comment_edit():
    if request.form['action'] == 'delete':
        comment = Comment.query.filter_by(id=int(request.form['id'])).first()
        db.session.delete(comment)
        db.session.commit()
    elif request.form['action'] == 'edit':
        comment = Comment.query.filter_by(id=int(request.form['id'])).first()
        comment.body = request.form['body'].strip()
        comment.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('comment'))

@app.route('/accept_new_project_edit',methods=['POST'])
def accept_new_project_edit():
    if request.form['action'] == 'delete':
        print 'delete'
    elif request.form['action'] == 'edit':
        project = Project.query.filter_by(id=int(request.form['id'])).first()
        project.project_name = request.form['title'].strip()
        project.project_body = request.form['body'].strip()
        project.project_credit = request.form['credit'].strip()
        project.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('accept_new_project'))

@app.route('/accept_modified_project_edit',methods=['POST'])
def accept_modified_project_edit():
    if request.form['action'] == 'delete':
        print 'delete'
    elif request.form['action'] == 'edit':
        project = Project.query.filter_by(id=int(request.form['id'])).first()
        project.project_name = request.form['title'].strip()
        project.project_body = request.form['body'].strip()
        project.project_credit = request.form['credit'].strip()
        project.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('accept_modified_project'))

@app.route('/accepted_project_edit',methods=['POST'])
def accepted_project_edit():
    if request.form['action'] == 'delete':
        print 'delete'
    elif request.form['action'] == 'edit':
        project = Project.query.filter_by(id=int(request.form['id'])).first()
        project.project_name = request.form['title'].strip()
        project.project_body = request.form['body'].strip()
        project.project_credit = request.form['credit'].strip()
        project.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('accepted_project'))

@app.route('/accept_new_product_edit',methods=['POST'])
def accept_new_product_edit():
    if request.form['action'] == 'delete':
        print 'delete'
    elif request.form['action'] == 'edit':
        print 'edit'
        product = Product.query.filter_by(id=int(request.form['id'])).first()
        product.product_name = request.form['product_name'].strip()
        product.product_desc = request.form['product_desc'].strip()
        product.product_price = request.form['product_price'].strip()
        product.product_color = request.form['product_color'].strip()
        product.product_size = request.form['product_size'].strip()
        product.product_model_name = request.form['product_model_name'].strip()
        product.product_meterial = request.form['product_meterial'].strip()
        product.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('accept_new_product'))

@app.route('/accept_modified_product_edit',methods=['POST'])
def accept_modified_product_edit():
    if request.form['action'] == 'delete':
        print 'delete'
    elif request.form['action'] == 'edit':
        print 'edit'
        product = Product.query.filter_by(id=int(request.form['id'])).first()
        product.product_name = request.form['product_name'].strip()
        product.product_desc = request.form['product_desc'].strip()
        product.product_price = request.form['product_price'].strip()
        product.product_color = request.form['product_color'].strip()
        product.product_size = request.form['product_size'].strip()
        product.product_model_name = request.form['product_model_name'].strip()
        product.product_meterial = request.form['product_meterial'].strip()
        product.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('accept_modified_product'))

@app.route('/accepted_product_edit',methods=['POST'])
def accepted_product_edit():
    if request.form['action'] == 'delete':
        print 'delete'
    elif request.form['action'] == 'edit':
        print 'edit'
        product = Product.query.filter_by(id=int(request.form['id'])).first()
        product.product_name = request.form['product_name'].strip()
        product.product_desc = request.form['product_desc'].strip()
        product.product_price = request.form['product_price'].strip()
        product.product_color = request.form['product_color'].strip()
        product.product_size = request.form['product_size'].strip()
        product.product_model_name = request.form['product_model_name'].strip()
        product.product_meterial = request.form['product_meterial'].strip()
        product.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('accepted_product'))
