#-*- coding:utf-8 -*-
from flask import Flask
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/test')
def test():
    return render_template('base.html')
