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

## 2015.08.18
