# Copyright (c) 2024 Luoyang Foreign Language School
# Copyright (C) 2024 bzy-080408<Bzy080408@outlook.com>

from gevent import pywsgi

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
import time

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

# ****************************************************
# 比赛配置
# ****************************************************

exam_name = "12.26模拟赛" # 比赛名称
exam_end_time = "2099/12/27 17:50:00" # 结束时间
exam_message = "密码:memory@2024" # 消息
problem1_name = "flower" # 第1题名称
problem2_name = "art" # 第2题名称
problem3_name = "contest" # 第3题名称
problem4_name = "plat" # 第3题名称
debug_flag = False # 是否开启测试测试,生产环境建议False
server_host = '127.0.0.1' # 服务器ip
max_code_size = 100 #最大上传代码大小，单位为kb

# Linux服务器注意:
# 若运行后提示没有权限(Permission denied),请以root安装requirements并启动

server_port = '5050' # 网站端口,默认HTTP为80,不建议启用HTTPS并使用443端口



def create_user(user_name, password):
    """创建一个用户"""
    user = {
        "name": user_name,
        "password": generate_password_hash(password),
        "id": uuid.uuid4()
    }
    USERS.append(user)

def load_exam():
    with open('uploads/warn_user.csv', 'a') as warn_user:
        csv_writer = csv.writer(warn_user)
        csv_writer.writerow(['准考证号', '试图上传文件的大小(单位kb)', '试图上传的时间', 'IP地址'])
        # warn_user.write('准考证号, 试图上传文件的大小(单位kb), \n')
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
#
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
                return render_template('/User/Notice.html', username=current_user.username, exam_name=exam_name, end_time=exam_end_time, exam_message=exam_message)
            else:
                #emsg = "用户名或密码密码有误"
                return "<script> alert(\"准考证号、身份证号或密码有误！\");window.open(\"/\");</script>"
    return render_template('index.html', form=form, emsg=emsg, exam_message=exam_message)

@app.route('/')  # 首页
# @login_required  # 需要登录才能访问
def index():
    #return render_template('index.html', username=current_user.username)
    return render_template('index.html', exam_name=exam_name, exam_message=exam_message)

@app.route('/static')
def staticfile(filename):
    return render_template('static/', filename)


# 代码下载更换到/static
# @app.route('/CompetitionFiles') 
# def paperfile(filename):
#     return render_template('./CompetitionFiles/', filename)


@app.route('/User/CodeUpload')
@login_required
def CodeUpload():
    codepath = "uploads/" +  current_user.username + "/"
    T1upload = os.path.exists(codepath + problem1_name + '/' + problem1_name + ".cpp")
    T2upload = os.path.exists(codepath + problem2_name + '/' + problem2_name + ".cpp")
    T3upload = os.path.exists(codepath + problem3_name + '/' + problem3_name + ".cpp")
    T4upload = os.path.exists(codepath + problem4_name + '/' + problem4_name + ".cpp")
    T1time = "None" # 默认时间军均为time 
    T2time = "None" 
    T3time = "None" 
    T4time = "None" 
    # 请务必确保服务器时间准确
    if T1upload:
        T1time =  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(codepath + problem1_name + '/' + problem1_name + ".cpp")))
    if T2upload:
        T2time =  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(codepath + problem2_name + '/' + problem2_name + ".cpp")))
    if T3upload:
        T3time =  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(codepath + problem3_name + '/' + problem3_name + ".cpp")))
    if T4upload:
        T4time =  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(codepath + problem4_name + '/' + problem4_name + ".cpp")))
    # os.path.exists(codepath);
    return render_template('/User/CodeUpload.html', username=current_user.username, exam_name=exam_name, end_time=exam_end_time, problem1_name=problem1_name, problem2_name=problem2_name, problem3_name=problem3_name, problem4_name=problem4_name, T1upload=T1upload, T2upload=T2upload, T3upload=T3upload, T4upload=T4upload, T1time=T1time, T2time=T2time, T3time=T3time, T4time=T4time)

@app.route('/User/download')
@login_required
def download():
    return render_template('/User/download.html', username=current_user.username, exam_name=exam_name, end_time=exam_end_time)

@app.route('/User/Notice')
@login_required
def Notice():
    return render_template('/User/Notice.html', username=current_user.username, exam_name=exam_name, end_time=exam_end_time, exam_message=exam_message)


@app.route('/User/LogOut')  # 登出
@login_required
def logout():
    logout_user()
    return render_template('index.html', exam_name=exam_name)
    # return redirect(url_for('index.html'))


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    uppath = "uploads/" +  current_user.username + "/"

    if 'file' not in request.files:
        return '无文件部分'
    file = request.files['file']
    file_size = file.seek(0, os.SEEK_END) / 1024 # 获取上传文件的大小，单位为kb

    if file_size > max_code_size: 
        with open('uploads/warn_user.csv', 'a') as warn_user:
            csv_writer = csv.writer(warn_user) # 以csv格式写入
            user_ip = request.remote_addr
            csv_writer.writerow([current_user.username, file_size, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), user_ip]) #准考证号，文件大小，上传时间

        return '警告:请遵守比赛要求，严禁提交非代码文件'
    if file.filename == problem1_name + ".cpp":
        uppath += problem1_name + "/"
    elif file.filename == problem2_name + ".cpp":
        uppath += problem2_name + "/"
    elif file.filename == problem3_name + ".cpp":
        uppath += problem3_name + "/"
    elif file.filename == problem4_name + ".cpp":
        uppath += problem4_name + "/"
    elif file.filename == '':
        return '没有可选择的文件'
    else:
        return '请确认上传文件命名是否正确' 
    if file:
        # 设置文件存储路径
        # uppath = "uploads/" +  current_user.username + "/"
        upload_path = os.path.join(uppath , file.filename)

        # 检测路径是否存在，不存在则创建
        if not os.path.exists(os.path.dirname(upload_path)):
            os.makedirs(os.path.dirname(upload_path))

        # 存储文件
        file.save(upload_path)
        return '文件上传成功'

if __name__ == '__main__':
    load_exam()
    if debug_flag:
        app.run(host=server_host, debug=debug_flag, port=server_port, threaded=True)
    else: 
        server = pywsgi.WSGIServer((server_host, int(server_port)), app)
        server.serve_forever()
    