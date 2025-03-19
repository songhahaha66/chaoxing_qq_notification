from datetime import datetime

import psycopg2


class PostgreSql:
    def __init__(self, host, port, user, password, database):
        self.conn = psycopg2.connect(f"host={host} port={port} user={user} password={password} dbname={database}")
        self.cur = self.conn.cursor()
    def select(self, query, data):
        self.cur.execute(query, data)
        return self.cur.fetchall()
    def insert(self, data, table):
        insert_query = f"INSERT INTO {table} (taskrefId, subject, homework_name, due_date, status, url) VALUES (%s, %s, %s, %s, %s, %s);"
        try:
            due_date = datetime.strptime(f"{datetime.now().year}-{data['deadline']}", '%Y-%m-%d %H:%M')
        except:
            due_date = None
        try:
            self.cur.execute(insert_query, (data['taskrefId'], data['subject'], data['homework_name'], due_date, data['homework_status'], data['url']))
        except:
            print(f"Insert {data['homework_name']} failed")
            return False
        self.conn.commit()
        return True
    def update(self, sql, data):
        self.cur.execute(sql, data)
        self.conn.commit()

    def __del__(self):
        self.cur.close()
        self.conn.close()

