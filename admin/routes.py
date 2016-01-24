# -*- coding:utf-8 -*-
from flask import Flask, url_for
from werkzeug import secure_filename
import utils
import os
import time
from sqlalchemy import func

from config import UPLOAD_FOLDER, HOWSMART_DATABASE_URI, HOWSMART_SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']   = HOWSMART_DATABASE_URI
app.config['SECRET_KEY']                = HOWSMART_SECRET_KEY
app.config['UPLOAD_FOLDER']             = UPLOAD_FOLDER

from models import db, User, Feed, Image, Comment, Company, Project, Project_has_feed, Pros_category, Company_has_pros_category, Feed_category, Product, Product_has_image, Shop_category, User_like_feed, Follow, Status, Tag

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
        d = {
                'company': company,
                'project': project,
                'user': user,
                'status_name' : status_name
                }
        ret.append(d)
    return ret

@app.route('/',methods=['GET','POST'])
def main():
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
    feeds = Feed.query.order_by(Feed.created_at.desc())
    feeds = get_feed_information(feeds)
    return render_template('photos.html',feeds=feeds)

@app.route('/pros')
def pros():
    pros = User.query.filter_by(level=2).order_by(User.created_at.desc()).all()
    pros = get_pros_information(pros)
    return render_template('pros.html',pros=pros)

@app.route('/shop')
def shop():
    products = Product.query.order_by(Product.created_at.desc()).all()
    products = get_shop_information(products)
    return render_template('shop.html',products=products)

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
        print 'delete'
    elif request.form['action'] == 'edit':
        feed = Feed.query.filter_by(id=int(request.form['id'])).first()
        feed.title = request.form['title'].strip()
        feed.body = request.form['body'].strip()
        feed.status_id = int(request.form['status'])
        db.session.commit()
    return redirect(url_for('photos'))


@app.route('/pros_edit',methods=['POST'])
def pros_edit():
    if request.form['action'] == 'delete':
        print 'delete'
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
        print 'delete'
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

@app.route('/comment_edit',methods=['POST'])
def comment_edit():
    if request.form['action'] == 'delete':
        print 'delete'
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
