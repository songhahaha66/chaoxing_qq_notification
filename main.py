import datetime
import configparser
import json
import time
from apscheduler.schedulers.background import BackgroundScheduler

import chaoxing_me
from chaoxing_me import *
from xxt_notify import send_qmsg
from postgres1 import PostgreSql

def load_tasks_from_db():
    """从数据库加载任务并调度"""
    all_homework = get_all_homework(db)
    for homework in all_homework:
        if homework['due_date'] and homework['status'] == "未提交" and not homework['schedule_task']:
            schedule_task(homework['taskrefId'], homework['due_date'])

def schedule_task(task_id, due_date):
    """根据截止时间调度任务"""
    notify_intervals = [2,1,0.5,0.3,0.1]
    for days in notify_intervals:
        notify_time = due_date - datetime.timedelta(days=days)
        if notify_time > datetime.datetime.now():
            job = scheduler.add_job(my_task, 'date', run_date=notify_time, args=[task_id, days, due_date])
            job_cache.setdefault(task_id, []).append(job)
    update_query = "UPDATE homework SET schedule_task = true WHERE taskrefId = %s;"
    db.update(update_query, (task_id,))
    print(f"任务添加成功，作业ID:{task_id}，截止时间:{due_date}")


def cancel_task(task_id):
    """取消定时任务"""
    if task_id in job_cache:
        for job in job_cache[task_id]:
            scheduler.remove_job(job.id)
        del job_cache[task_id]

def my_task(task_id, remain_time, due_time):
    """作业截止时间触发的任务"""
    query = "SELECT * FROM homework WHERE taskrefId = %s;"
    result = db.select(query, (task_id,))
    homework_name = result[0][2]
    homework_subject = result[0][1]
    send_qmsg(f"你的作业 {homework_name}({homework_subject}) 截止时间为{due_time}，还有{float(remain_time)*24}小时！")

def get_all_homework(db):
    query = "SELECT * FROM homework;"
    results = db.select(query, ())
    return [dict(taskrefId=row[0], subject=row[1], homework_name=row[2], due_date=row[3], status=row[4], url=row[5],schedule_task=row[8]) for row in results]

def get_and_update_data(xxt, db):
    all_homework = xxt.get_all_homework()
    all_homework_sql = get_all_homework(db)
    for homework in all_homework_sql:
        try:
            if homework['detail_url'] is None and homework['status'] =='未提交':
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
        index = next((i for i, hw in enumerate(all_homework_sql) if str(hw['taskrefId']) == homework['taskrefId']), None)
        if index is not None and homework['homework_status'] != "未提交" and all_homework_sql[index]['status'] == '未提交':
            update_query = "UPDATE homework SET status = %s, updated_at = %s WHERE taskrefId = %s;"
            db.update(update_query, (homework['homework_status'], datetime.datetime.now(), homework['taskrefId']))
            print(f"Update {homework['homework_name']} successfully")
            cancel_task(homework['taskrefId'])
        elif index is None:
            try:
                homework_copy['due_date'] = datetime.datetime.strptime(f"{datetime.datetime.now().year}-{homework['deadline']}", '%Y-%m-%d %H:%M')
            except:
                homework_copy['due_date'] = None
            result = db.insert(homework_copy, "homework")
            if result:
                print(f"Insert {homework['homework_name']} successfully")
                if homework_copy['due_date']:
                    print("提交时间：", homework_copy['due_date'])
        else:
            print(f"{homework['homework_name']} already exists")

def start_program():
    """用于启动任务和周期性更新"""
    global xxt, db
    xxt = chaoxing_me.xxt(chaoxing_account, chaoxing_password)
    db = PostgreSql(sql_host, sql_port, sql_user, sql_password, sql_database)
    get_and_update_data(xxt, db)
    load_tasks_from_db()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("./config.ini", encoding="utf-8")
    chaoxing_account = config.get("chaoxing", "account")
    chaoxing_password = config.get("chaoxing", "password")
    sql_host = config.get("database", "endpoint")
    sql_port = config.get("database", "port")
    sql_user = config.get("database", "username")
    sql_password = config.get("database", "password")
    sql_database = config.get("database", "database")
    scheduler = BackgroundScheduler()
    scheduler.start()
    job_cache = {}  # 存储已调度的作业任务 {作业ID: 任务对象}
    scheduler.add_job(start_program, 'interval', hours=4, next_run_time=datetime.datetime.now())
    try:
        while True:
            time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down...")
        scheduler.shutdown()
