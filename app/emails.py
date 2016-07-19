#!/usr/bin/python
#-*- coding:utf-8 -*-
from flask import render_template
from flask.ext.mail import Message
from decorators import async
from routes.app import app
from app import mail

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app,msg)

if __name__ == '__main__':
    send_email('test',
            'sisobus1@gmail.com',
            ['sisobus1@gmail.com'],
            'test',
            'test')
