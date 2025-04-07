import datetime
import configparser
import time
from apscheduler.schedulers.background import BackgroundScheduler

import chaoxing_me
from chaoxing_me import *
from xxt_notify import send_qmsg
from postgres1 import PostgreSql

config = configparser.ConfigParser()
config.read("./config.ini", encoding="utf-8")

account = config.get("chaoxing", "account")
password = config.get("chaoxing", "password")
sql_host = config.get("database", "endpoint")
sql_port = config.get("database", "port")
sql_user = config.get("database", "username")
sql_password = config.get("database", "password")
sql_database = config.get("database", "database")

remain_days = [float(x) for x in config.get("notify","remain_days").split(",")]

def schedule_task(task_id, due_date):
    for d in remain_days:
        notify_time = due_date - datetime.timedelta(days=d)
        if notify_time > datetime.datetime.now():
            job = scheduler.add_job(my_task, 'date', run_date=notify_time, args=[task_id, d,due_date])
            job_cache.setdefault(task_id, []).append(job)

def cancel_task(task_id):
    """取消定时任务"""
    if task_id in job_cache:
        for job in job_cache[task_id]:
            scheduler.remove_job(job.id)
        del job_cache[task_id]

def my_task(task_id, remain_time,due_time):
    """作业截止时间触发的任务"""
    query = "SELECT * FROM homework WHERE taskrefId = %s;"
    result = db.select(query, (task_id,))
    homework_name = result[0][2]
    homework_subject = result[0][1]
    send_qmsg(f"你的作业 {homework_name}({homework_subject}) 截止时间为{due_time}，还有{float(remain_time)*24}小时！")

def get_all_homework(db):
    query = "SELECT * FROM homework;"
    results = db.select(query, ())
    return [dict(taskrefId=row[0], subject=row[1], homework_name=row[2], due_date=row[3], status=row[4], url=row[5]) for row in results]

def get_and_update_data():
    all_homework = xxt.get_all_homework()
    all_homework_sql = get_all_homework(db)
    for homework in all_homework:
        homework_copy = homework.copy()
        index = next((i for i, hw in enumerate(all_homework_sql) if str(hw['taskrefId']) == homework['taskrefId']), None)
        if index is not None and homework['homework_status'] != "未提交" and all_homework_sql[index]['status'] == "未提交":
            update_query = "UPDATE homework SET status = %s, updated_at = %s WHERE taskrefId = %s;"
            db.update(update_query, (homework['homework_status'], datetime.datetime.now(), homework['taskrefId']))
            print(f"Update {homework['homework_name']} successfully")
            cancel_task(homework['taskrefId'])
        elif index is None:
            try:
                homework_copy['due_date'] = datetime.datetime.strptime(f"{datetime.datetime.now().year}-{homework['deadline']}",'%Y-%m-%d %H:%M')
            except:
                homework_copy['due_date'] = None
            result = db.insert(homework_copy, "homework")
            if result:
                print(f"Insert {homework['homework_name']} successfully")
                if homework_copy['due_date']:
                    print("提交时间：", homework_copy['due_date'])
                    schedule_task(homework_copy['taskrefId'], homework_copy['due_date'])
        else:
            print(f"{homework['homework_name']} already exists")

def start_program():
    """用于启动任务和周期性更新"""
    global xxt
    xxt = chaoxing_me.xxt(account, password)
    get_and_update_data()


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.start()
    job_cache = {}  # 存储已调度的作业任务 {作业ID: 任务对象}
    db = PostgreSql(sql_host, sql_port, sql_user, sql_password, sql_database)
    scheduler.add_job(start_program, 'interval', hours=4,next_run_time=datetime.datetime.now())
    try:
        while True:
            time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down...")
        scheduler.shutdown()
