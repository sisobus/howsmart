#!/usr/bin/python
from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

from __init__ import app
from models import db, User

def test():
    print db.session
    if db.session.query('1').from_statement('select 1').all():
        print 'it works!!!'
    else :
        print 'not works!!!'

if __name__ == '__main__':
    test()

