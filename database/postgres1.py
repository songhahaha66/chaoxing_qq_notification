from datetime import datetime

import psycopg2


class PostgreSql:
    def __init__(self, host, port, user, password, database):
        self.conn = psycopg2.connect(f"host={host} port={port} user={user} password={password} dbname={database}")
        self.cur = self.conn.cursor()
    def query(self, table):
        self.cur.execute(f"select * from {table}")
        return self.cur.fetchall()
    def insert(self, data, table):
        insert_query = f"INSERT INTO {table} (taskrefId, subject, homework_name, due_date, status, url) VALUES (%s, %s, %s, %s, %s, %s);"
        for i in data:
            try:
                due_date = datetime.strptime(f"{datetime.now().year}-{i['deadline']}", '%Y-%m-%d %H:%M')
            except:
                due_date = None
            try:
                self.cur.execute(insert_query, (i['taskrefId'], i['subject'], i['homework_name'], due_date, i['homework_status'], i['url']))
            except:
                pass
            self.conn.commit()
    def update(self, sql):
        self.cur.execute(sql)
        self.conn.commit()
    def __del__(self):
        self.cur.close()
        self.conn.close()

