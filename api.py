import configparser
import json
from typing import Union
from datetime import datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

import chaoxing_me
from postgres1 import PostgreSql
from fastapi.middleware.cors import CORSMiddleware

class ChaoxingAccount(BaseModel):
    chaoxing_account: str
    chaoxing_password: str
class Account(BaseModel):
    chaoxing_account: str
    chaoxing_password: str
class RefreshTokenRequest(BaseModel):
    refresh_token: str
app = FastAPI()

config = configparser.ConfigParser()
config.read("./config.ini", encoding="utf-8")

chaoxing_account = config.get("chaoxing", "account")
chaoxing_password = config.get("chaoxing", "password")

auth_account = config.get("auth", "username")
auth_password = config.get("auth", "password")

sql_host = config.get("database", "endpoint")
sql_port = config.get("database", "port")
sql_user = config.get("database", "username")
sql_password = config.get("database", "password")
sql_database = config.get("database", "database")

db = PostgreSql(sql_host, sql_port, sql_user, sql_password, sql_database)

SECRET_KEY = config.get("auth", "SECRET_KEY")
ALGORITHM = config.get("auth", "algorithm")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    'http://songhahaha1.eastasia.cloudapp.azure.com',
    'http://localhost:5173',
    'http://homework.songhahaha.top'
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#TODO数据库第二页
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """生成 JWT 令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """生成刷新令牌，并在令牌中添加 type 字段"""
    to_encode = data.copy()
    to_encode.update({"type": "refresh"})
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    refresh_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_jwt

def verify_token(token: str):
    """验证 JWT 令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except InvalidTokenError and ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_refresh_token(token: str):
    """验证刷新令牌，确保令牌有效且为刷新类型"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="不是合法的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="刷新令牌无效",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except (InvalidTokenError, ExpiredSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_all_homework_list(db):
    query = "SELECT * FROM homework;"
    results = db.select(query, ())
    return [dict(taskrefId=row[0], subject=row[1], homework_name=row[2], due_date=row[3], status=row[4], url=row[5],schedule_task=row[8],detail_url=row[9],detail_info=row[10]) for row in results]



def get_and_update_homework_list(xxt, db):
    all_homework = xxt.get_all_homework()
    all_homework_sql = get_all_homework_list(db)
    for homework in all_homework_sql:
        try:
            if homework['detail_url'] is None:
                homework['detail_url'] = xxt.get_homework_detail_url(homework['url'])
                homework['detail_info'] = xxt.get_homework_detail_info(homework['detail_url'])
                json_data = json.dumps(homework['detail_info'])
                if homework['detail_url']:
                    update_query = "UPDATE homework SET detail_url = %s,detail_info = %s WHERE taskrefId = %s;"
                    db.update(update_query, (homework['detail_url'], json_data,homework['taskrefId']))
                    print(f"Update {homework['homework_name']} detail url successfully")
        except:
            print(f"Failed to update {homework['homework_name']} detail url")

    for homework in all_homework:
        homework_copy = homework.copy()
        index = next((i for i, hw in enumerate(all_homework_sql) if str(hw['taskrefId']) == homework['taskrefId']),
                     None)
        if index is not None and homework['homework_status'] != "未提交" and all_homework_sql[index]['status'] == '未提交':
            update_query = "UPDATE homework SET status = %s, updated_at = %s WHERE taskrefId = %s;"
            db.update(update_query, (homework['homework_status'], datetime.now(), homework['taskrefId']))
            print(f"Update {homework['homework_name']} successfully")
        elif index is None:
            print(homework)
            try:
                homework_copy['due_date'] = datetime.strptime(
                    f"{datetime.now().year}-{homework['deadline']}", '%Y-%m-%d %H:%M')
            except:
                homework_copy['due_date'] = None
            result = db.insert(homework_copy, "homework")
            if result:
                print(f"Insert {homework['homework_name']} successfully")
                if homework_copy['due_date']:
                    print("提交时间：", homework_copy['due_date'])
        else:
            print(f"{homework['homework_name']} already exists")


# 文件：api.py
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """登录并生成访问令牌和刷新令牌"""
    if form_data.username == auth_account and form_data.password == auth_password:
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": form_data.username, "type": "access"},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": form_data.username})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 文件：api.py
@app.post("/refresh-token")
def refresh_access_token(refresh_req: RefreshTokenRequest):
    """通过刷新令牌获取新的访问令牌"""
    username = verify_refresh_token(refresh_req.refresh_token)
    access_token_expires = timedelta(minutes=30)
    new_access_token = create_access_token(
        data={"sub": username, "type": "access"},
        expires_delta=access_token_expires
    )
    return {"access_token": new_access_token, "token_type": "bearer"}

@app.get("/get/homework")
def query_homework(page: int = 1, page_size: int = 10, token: str = Depends(oauth2_scheme)):
    """查询作业详情（需要验证令牌）"""
    verify_token(token)
    count_result = db.select("SELECT COUNT(*) FROM homework;", ())
    total_count = count_result[0][0]
    total_pages = (total_count + page_size - 1) // page_size
    query = "SELECT * FROM homework ORDER BY created_at DESC LIMIT %s OFFSET %s;"
    results = db.select(query, (page_size, (page - 1) * page_size))
    return_data = {
        "page": page,
        "total_pages":total_pages ,
        "total_count": total_count,
        "data": [dict(taskrefId=row[0], subject=row[1], homework_name=row[2], due_date=row[3], status=row[4], url=row[5],detail_url=row[9]) for row in results]
    }
    return return_data
@app.get("/get/homework/{taskrefId}")
def query_homework_by_id(taskrefId: str, token: str = Depends(oauth2_scheme)):
    """根据作业 ID 查询作业详情（需要验证令牌）"""
    verify_token(token)
    query = "SELECT * FROM homework WHERE taskrefId = %s;"
    result = db.select(query, (taskrefId,))
    if result:
        return {"data": dict(taskrefId=result[0][0], subject=result[0][1], homework_name=result[0][2], due_date=result[0][3], status=result[0][4], url=result[0][5],detail_url=result[0][9],detail_info=result[0][10])}
    else:
        raise HTTPException(status_code=404, detail="Homework not found")

@app.post("/update/account")
def update_account(Account: ChaoxingAccount, token: str = Depends(oauth2_scheme)):
    """更新学习通账号密码（需要验证令牌）"""
    verify_token(token)
    global chaoxing_account, chaoxing_password
    config.set("chaoxing", "account", Account.account)
    config.set("chaoxing", "password", Account.password)
    with open("./config.ini", "w") as configfile:
        config.write(configfile)
    config.read("./config.ini", encoding="utf-8")
    chaoxing_account = config.get("chaoxing", "account")
    chaoxing_password = config.get("chaoxing", "password")
    return {"message": "Account updated successfully"}

@app.get("/update/homework")
def update_homework(token: str = Depends(oauth2_scheme)):
    """更新作业（需要验证令牌）"""
    verify_token(token)
    xxt = chaoxing_me.xxt(chaoxing_account, chaoxing_password)
    get_and_update_homework_list(xxt,db)
    return {"code":1,"message": "Homework updated successfully"}