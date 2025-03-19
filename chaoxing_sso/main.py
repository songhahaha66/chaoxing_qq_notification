from chaoxing_sso.chaoxing_me import *
from chaoxing_sso.xxt_notify import send_qmsg

config = configparser.ConfigParser()
config.read("./config.ini",encoding="utf-8")
account=config.get("chaoxing","account")
password=config.get("chaoxing","password")
a = xxt(account,password)
all_homework = a.get_all_homework()
for i in all_homework:
    if i['homework_status'] == "未提交":
        send_qmsg(f"你有未提交的作业：{i['subject']}:{i['homework_name']},截止时间：{i['deadline']}")