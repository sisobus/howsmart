#-*- coding:utf-8 -*-
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import routes

#@app.route('/signup', methods=['GET', 'POST'])
#def signup():
#    form = SignupForm()
#
#    if request.method == 'POST':
#        if form.validate() == False:
#            return render_template('test.html', form=form)
#        else :
#            return "[1] Create a new user [2] sign in the user [3] redirect to the user's profile"
#    elif request.method == 'GET':
#        return render_template('test.html', form=form)
