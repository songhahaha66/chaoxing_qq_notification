# 超星学习通自动获取作业并提醒

## 注意：
经过测试：阿里云北京被学习通屏蔽，无法使用程序

## 配置

### 安装数据库
请安装PostgreSQL，创建数据表homework

```postgresql
CREATE TABLE homework  (
  taskrefId SERIAL PRIMARY KEY,
  subject VARCHAR(255) NOT NULL,
  homework_name TEXT NOT NULL,
  due_date TIMESTAMP,
  status TEXT NOT NULL,
  url TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  schedule_task BOOL,
  detail_url TEXT,
  detail_info TEXT
);
```

### 配置Napcat

本项目使用QQ机器人进行消息推送，请自行安装Napcat并设置Token。

### 配置config.ini

创建文件config.ini

示例如下

```
[chaoxing] ;超星账户密码
account=
password=
[napcat] ;Napcat密钥和服务器地址
token = 
host = 
[database] ;数据库
endpoint =
username =
password =
port =
database =
[qq] ;要发送通知的QQ号
number =
[notify] ;距离作业截止提交发送通知的时间（单位：天）
remain_days = 0.5,1,2
[auth] ;API认证账户（使用API必须）
username =
password =
SECRET_KEY =
algorithm =

```

### 安装必要的库

```
pip install -r requirements.txt
```

## 运行

本项目通知系统和前端网页分离，可以只部署通知系统。

### 通知系统

在目录运行

```
python3 main.py
```

即可

### 前端

#### 配置api

安装uvicorn

```
pip install "uvicorn[standard]"
```

运行api.py

```
uvicorn api:app --host 0.0.0.0 --port 8080 --reload
```

#### 配置网页

修改/frontend/.env

```
VITE_API_BASE_URL=
```

改成你的后端地址

在frontend目录下，使用

```
pnpm i
pnpm run build
```

编译，把生成的网页挂到服务器即可。

### 

