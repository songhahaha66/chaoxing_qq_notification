from datetime import datetime

from chaoxing_sso.chaoxing_me import *
from chaoxing_sso.xxt_notify import send_qmsg
from database.postgres1 import PostgreSql
config = configparser.ConfigParser()
config.read("./config.ini",encoding="utf-8")

account=config.get("chaoxing","account")
password=config.get("chaoxing","password")
sql_host = config.get("database","endpoint")
sql_port = config.get("database","port")
sql_user = config.get("database","username")
sql_password = config.get("database","password")
sql_database = config.get("database","database")

a = xxt(account,password)
all_homework = a.get_all_homework()
print(all_homework)
db = PostgreSql(sql_host,sql_port,sql_user,sql_password,sql_database)

for homework in all_homework:
    result = db.insert(homework, "homework")
    if result:
        print(f"Insert {homework['homework_name']} successfully")
    else:
        db.conn.rollback()
        update_query = "UPDATE homework SET status = %s,updated_at = %s WHERE taskrefId = %s;"
        db.update(update_query, (homework['homework_status'], datetime.now(), homework['taskrefId']))
        print(f"Update {homework['homework_name']} successfully")

"""for i in all_homework:
    if i['homework_status'] == "未提交":
        #send_qmsg(f"你有未提交的作业：{i['subject']}:{i['homework_name']},截止时间：{i['deadline']}")
        pass"""