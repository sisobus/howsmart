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

"`
    $ virtualenv venv
    $ . venv/bin/activate
    $ sudo pip install flask
    $ pip freeze > requirement.txt
"`

