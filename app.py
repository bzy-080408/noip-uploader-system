# Copyright (c) 2024 Luoyang Foreign Language School
# Copyright (C) 2024 bzy-080408<Bzy080408@outlook.com>

from flask import Flask, render_template, redirect, url_for, request

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from flask_login import LoginManager, UserMixin, current_user
from flask_login import logout_user, login_user, login_required

import uuid

import os
import csv


app = Flask(__name__)  # 创建 Flask 应用

app.secret_key = 'abc'  # 设置表单交互密钥

login_manager = LoginManager()  # 实例化登录管理对象
login_manager.init_app(app)  # 初始化应用
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'  # 设置用户登录视图函数 endpoint

# 用户数据
USERS = [ # 用户数据，TEST_USER为测试用户
    {
        "id": 1, 
        "name": 'TEST_USER',
        "password": generate_password_hash('TEST_USER')
    },
]

exam_name = "CCF河南省选Day1" # 比赛名称
exam_end_time = "2099/12/7 08:50:00" # 结束时间

problem1_name = "T1" #第1题名称
problem2_name = "T2" #第2题名称
problem3_name = "T3" #第3题名称
problem4_name = "T4" #第4题名称
def create_user(user_name, password):
    """创建一个用户"""
    user = {
        "name": user_name,
        "password": generate_password_hash(password),
        "id": uuid.uuid4()
    }
    USERS.append(user)

def load_exam():
    userconfig = open('config/user.csv')
    csv_reader1 = csv.reader(userconfig)
    for line in csv_reader1:
        create_user(line[0],line[1])
    #    print(line[2])

def get_user(user_name):
    """根据用户名获得用户记录"""
    for user in USERS:
        if user.get("name") == user_name:
            return user
    return None

class LoginForm(FlaskForm):
    """登录表单类"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])

class SignupForm(FlaskForm):
    """用户注册表单类"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', [
        DataRequired(),
        EqualTo('confirm', message='两次输入的密码不一致')
    ])
    confirm = PasswordField('确认密码')

class User(UserMixin):
    """用户类"""
    def __init__(self, user):
        self.username = user.get("name")
        self.password_hash = user.get("password")
        self.id = user.get("id")

    def verify_password(self, password):
        """密码验证"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """获取用户ID"""
        return self.id

    @staticmethod
    def get(user_id):
        """根据用户ID获取用户实体，为 login_user 方法提供支持"""
        if not user_id:
            return None
        for user in USERS:
            if user.get('id') == user_id:
                return User(user)
        return None

@login_manager.user_loader  # 定义获取登录用户的方法
def load_user(user_id):
    return User.get(user_id)


# @app.route('/signup/', methods=('GET', 'POST'))  # 注册
# def signup():
#     form = SignupForm()
#     emsg = None
#     if form.validate_on_submit():
#         user_name = form.username.data
#         password = form.password.data

#         user_info = get_user(user_name)  # 用用户名获取用户信息
#         if user_info is None:
#             create_user(user_name, password)  # 如果不存在则创建用户
#             return redirect(url_for("login"))  # 创建后跳转到登录页
#         else:
#             emsg = "用户名已存在"  # 如果用户已存在则给出错误提示
#     return render_template('signup.html', form=form, emsg=emsg)

@app.route('/login', methods=['POST'])  # 登录
def login():
    form = LoginForm()
    emsg = None
    #if form.validate_on_submit():
    if True:    
        user_name = request.form.get("name", "")
        password = request.form.get("password", "")
        idCard = request.form.get("idCard", "")
        user_info = get_user(user_name)
        if user_info is None:
            #emsg = "用户名"
            return "<script> alert(\"准考证号、身份证号或密码有误！\");window.open(\"/\");</script>"
        else:
            user = User(user_info)
            if user.verify_password(password):
                login_user(user)
                return render_template('/User/Notice.html', username=current_user.username, exam_name=exam_name, end_time=exam_end_time)
            else:
                #emsg = "用户名或密码密码有误"
                return "<script> alert(\"准考证号、身份证号或密码有误！\");window.open(\"/\");</script>"
    return render_template('index.html', form=form, emsg=emsg)

@app.route('/')  # 首页
# @login_required  # 需要登录才能访问
def index():
    #return render_template('index.html', username=current_user.username)
    return render_template('index.html', exam_name=exam_name)

@app.route('/static')
def staticfile(filename):
    return render_template('static/', filename)

@app.route('/User/CodeUpload')
@login_required
def CodeUpload():
    codepath = "uploads/" +  current_user.username + "/";
    # os.path.exists(codepath);
    return render_template('/User/CodeUpload.html', username=current_user.username, exam_name=exam_name, end_time=exam_end_time)

@app.route('/User/download')
@login_required
def download():
    return render_template('/User/download.html', username=current_user.username, exam_name=exam_name, end_time=exam_end_time)

@app.route('/User/Notice')
@login_required
def Notice():
    return render_template('/User/Notice.html', username=current_user.username, exam_name=exam_name, end_time=exam_end_time)


@app.route('/User/LogOut')  # 登出
@login_required
def logout():
    logout_user()
    return render_template('index.html', exam_name=exam_name)
    # return redirect(url_for('index.html'))


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return '无文件部分'

    file = request.files['file']

    if file.filename == '':
        return '没有可选择的文件'

    if file:
        # 设置文件存储路径
        uppath = "uploads/" +  current_user.username + "/";
        upload_path = os.path.join(uppath , file.filename)

        # 检测路径是否存在，不存在则创建
        if not os.path.exists(os.path.dirname(upload_path)):
            os.makedirs(os.path.dirname(upload_path))

        # 存储文件
        file.save(upload_path)
        return '文件已上传'

if __name__ == '__main__':
    load_exam()
    app.run(debug=True, port=5050, threaded=True)