# howsmart

## 2015.08.17
개발 첫 날, 환경설정을 했다.
- howsmart adduser 후 sudoer 권한 줌
- aptitude 를 이용해서 아래 프로그램을 설치함
    - python-pip
    - virtualenv
    - git
    - nginx
    - uwsgi
    - uwsgi-plugin-python
    - mysql-client
    - mysql-server
- virtualenv 로 개발 환경 만듬

```
    $ virtualenv venv
    $ . venv/bin/activate
    $ sudo pip install flask
    $ pip freeze > requirement.txt
```
- run.py, app/__init__.py, app/templates/ 만들어서 테스트 해봄
- howsmart_nginx.conf nginx config 파일을 생성
- /etc/nginx/sites-enabled/default 삭제
- symbolic link 걸어줌
```
    $ ln -s /home/howsmart/howsmart/howsmart_nginx.conf /etc/nginx/conf.d
```
- /etc/uwsgi/app-enabled/uwsgi.ini uwsgi 설정 파일 생성
```
[uwsgi]
base = /home/howsmart/howsmart

#location of the flask application file
file = /home/howsmart/howsmart/run.py
uid = www-data
gid = www-data

#uwsgi varible only, does not relate to your flask application
callable = app

#uwsgi plugins
plugins = python

#to create within a virtual environment
home = %(base)/venv

pythonpath = %(base)
socket = /tmp/%n.sock
logto = /var/log/uwsgi/%n.log
workers = 3
```
- uwsgi 랑 nginx restart
```
    $ sudo service uwsgi restart
    $ sudo service nginx restart
```

## 2015.08.18
navigation bar, main page banner를 추가했다.

- assets 위치를 잡을 수 있도록 howsmart_nginx.conf 파일을 수정했다.
```
    location /assets/ {
        alias /home/howsmart/howsmart/app/assets/;
    }
```
- navbar의 색을 #ffffff로 하고, body의 background-color를 #f5f5f5로 설정했다.
- 기본 글씨색을 #666으로 설정했다. 
- http://code.tutsplus.com/tutorials/intro-to-flask-signing-in-and-out--net-29982 
    - 여기 참고해서 login 구현하면 될 듯
    - flask-login 모듈 사용

### To do
- login, logout, sign up, fb-login

## 2015.08.19
- aptitude 를 이용하여 다음 프로그램을 설치함
    - libmysqlclient-dev
- venv 에 mysql-python 을 설치함
- mysql default character set을 utf8 로 설정(한글깨짐방지)
    - /etc/mysql/my.cnf
    - test : show variables like 'c%';

```
#
# The MySQL database server configuration file.
#
# You can copy this to one of:
# - "/etc/mysql/my.cnf" to set global options,
# - "~/.my.cnf" to set user-specific options.
# 
# One can use all long options that the program supports.
# Run program with --help to get a list of available options and with
# --print-defaults to see which it would actually understand and use.
#
# For explanations see
# http://dev.mysql.com/doc/mysql/en/server-system-variables.html

# This will be passed to all mysql clients
# It has been reported that passwords should be enclosed with ticks/quotes
# escpecially if they contain "#" chars...
# Remember to edit /etc/mysql/debian.cnf when changing the socket location.
[client]
port            = 3306
socket          = /var/run/mysqld/mysqld.sock

# Here is entries for some specific programs
# The following values assume you have at least 32M ram

# This was formally known as [safe_mysqld]. Both versions are currently parsed.
[mysqld_safe]
socket          = /var/run/mysqld/mysqld.sock
nice            = 0

[mysqld]
#
# * Basic Settings
#
character-set-client-handshake=FALSE
init_connect="SET collation_connection = utf8_general_ci"
init_connect="SET NAMES utf8"
character-set-server = utf8
collation-server = utf8_general_ci

user            = mysql
pid-file        = /var/run/mysqld/mysqld.pid
socket          = /var/run/mysqld/mysqld.sock
port            = 3306
basedir         = /usr
datadir         = /var/lib/mysql
tmpdir          = /tmp
lc-messages-dir = /usr/share/mysql
skip-external-locking
#
# Instead of skip-networking the default is now to listen only on
# localhost which is more compatible and is not less secure.
bind-address            = 127.0.0.1
#
# * Fine Tuning
#
key_buffer              = 16M
max_allowed_packet      = 16M
thread_stack            = 192K
thread_cache_size       = 8
# This replaces the startup script and checks MyISAM tables if needed
# the first time they are touched
myisam-recover         = BACKUP
#max_connections        = 100
#table_cache            = 64
#thread_concurrency     = 10
#
# * Query Cache Configuration
#
query_cache_limit       = 1M
query_cache_size        = 16M
#
# * Logging and Replication
#
# Both location gets rotated by the cronjob.
# Be aware that this log type is a performance killer.
# As of 5.1 you can enable the log at runtime!
#general_log_file        = /var/log/mysql/mysql.log
#general_log             = 1
#
# Error log - should be very few entries.
#
log_error = /var/log/mysql/error.log
#
# Here you can see queries with especially long duration
#log_slow_queries       = /var/log/mysql/mysql-slow.log
#long_query_time = 2
#log-queries-not-using-indexes
#
# The following can be used as easy to replay backup logs or for replication.
# note: if you are setting up a replication slave, see README.Debian about
#       other settings you may need to change.
#server-id              = 1
#log_bin                        = /var/log/mysql/mysql-bin.log
expire_logs_days        = 10
max_binlog_size         = 100M
#binlog_do_db           = include_database_name
#binlog_ignore_db       = include_database_name
#
# * InnoDB
#
# InnoDB is enabled by default with a 10MB datafile in /var/lib/mysql/.
# Read the manual for more InnoDB related options. There are many!
#
# * Security Features
#
# Read the manual, too, if you want chroot!
# chroot = /var/lib/mysql/
#
# For generating SSL certificates I recommend the OpenSSL GUI "tinyca".
#
# ssl-ca=/etc/mysql/cacert.pem
# ssl-cert=/etc/mysql/server-cert.pem
# ssl-key=/etc/mysql/server-key.pem



[mysqldump]
quick
quote-names
max_allowed_packet      = 16M

[mysql]
#no-auto-rehash # faster start of mysql but no tab completition

[isamchk]
key_buffer              = 16M

#
# * IMPORTANT: Additional settings that can override those from this file!
#   The files must end with '.cnf', otherwise they'll be ignored.
#
!includedir /etc/mysql/conf.d/
```

- 로그인 구현을 위하여 db modeling 을 함
![alt tag](http://1.234.80.248/assets/images/db_modeling.png)
- mysql 에 모델링한 db를 올림

### To do
- sign up, sign in을 꼭 구현해야 함.
    - http://code.tutsplus.com/tutorials/intro-to-flask-signing-in-and-out--net-29982
    - https://github.com/maxcountryman/flask-login/wiki/A-simple-working-demo
    - 둘을 참고하되 flask-wtf를 쓰지않고, form을 넘겨서 구현하는 방식으로 해야함

## 2015.08.25
로그인을 구현했다.
- flask-wtf 를 사용함
- flask-Login 을 이용했기 때문에 injection은 문제없을듯

## 2015.08.26
feed 쓰는 페이지를 생성했다.
- image_container 는 스크롤이 되지 않고, content_container 만 스크롤 되게 하기 힘들었다.
- content_container 의 크기를 300px 로 고정시키고, image_container를 relative 로 주려했으나 실패! 그 후 70:30%로 fix함
    - 고쳐야 되면 나중에 고치도록 하자!

### To do
- forms.py 에 wrtieFeedForm 을 추가한다.
- write_feed.html에 적용한 뒤 db 등록
- image 추가 및 등록은 추후에 하도록 한다.
    - 아직 image에 태깅을 어떻게 해야할지 감이안옴.
    - 일단은 tag에 x,y좌표값을 저장하는 생각을 해봤으나 조금더 관련 라이브러리를 찾아봐야함.
- feed_detail 페이지를 만든다.
    - 아마 write_feed 페이지와 거의 유사할 것 같으므로 write_feed만 끝나면 쉽게할 수 있을듯

## 2015.08.26
file upload를 구현하고 추후 드랍다운 및 프리뷰를 어떻게 할지 결정함
- file은 app/files 에 저장하기로 하고, 디비에 path를 저장함
- drag & drop이 가능하게 하기 위하여 관련 jquery 라이브러리를 찾음
    - dropzone.js 가 drag & drop과 프리뷰를 지원함
    - http://www.dropzonejs.com/
    - https://github.com/moremorefor/flask-fileupload-dropzonejs : flask + dropzone example

### To do
- 원래 오늘 하려 했던 위쪽 to do를 상속한다.
    - forms.py 에 writeFeedForm 을 추가한다.
    - write_feed.html에 적용한 뒤 db등록
    - feed_detail.html 페이지를 만든다.
- image file upload를 dropzonejs를 이용하여 구현한다.
    - image_container 에 적용하면 될 듯
    - content_form_container 를 이쁘게 구현해야 함

## 2015.08.29
write_fedd page 어느정도 완성
- jquery를 이용하여 간단하게 preview 구현
- WriteFeedForm 추가

## 2015.09.01
feed_detail 페이지를 추가했다.
- css의 수정 필요
- 태깅 필요