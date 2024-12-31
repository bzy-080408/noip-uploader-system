# 试题存储

/static/download.zip

# 导入用户

参考config/user.csv

# 修改比赛相关

app.py中修改对应内容

# 安装使用

```bash
sudo apt install python3 python3-pip
pip3 install -r requirements.txt
python3 app.py
```

# 目录

* /config 设置
* /static 静态文件（js,css)
* /templates html文件目录
* /uploads 考生代码上传目录

# 上传文件的说明：

准考证号目录下直接存放代码，针对OI赛制测评请额外新建文件夹并移动源代码

## 违规考生名单:

**文件位置**:/uploads/warn_user.csv
