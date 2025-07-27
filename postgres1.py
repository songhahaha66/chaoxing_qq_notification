from datetime import datetime

import psycopg2


class PostgreSql:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = psycopg2.connect(f"host={self.host} port={self.port} user={self.user} password={self.password} dbname={self.database}")
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def reconnect(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        self.conn = psycopg2.connect(f"host={self.host} port={self.port} user={self.user} password={self.password} dbname={self.database}")
        self.cur = self.conn.cursor()

    def select(self, query, data, retries=3):
        for _ in range(retries):
            try:
                self.cur.execute(query, data)
                return self.cur.fetchall()
            except psycopg2.InterfaceError:
                print("Database connection error")
                self.reconnect()
        raise psycopg2.InterfaceError("Failed after multiple retries")
            
    def insert(self, data, table):
        insert_query = f"INSERT INTO {table} (taskrefId, subject, homework_name, due_date, status, url) VALUES (%s, %s, %s, %s, %s, %s);"
        try:
            self.cur.execute(insert_query, (data['taskrefId'], data['subject'], data['homework_name'], data['due_date'], data['homework_status'], data['url']))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Insert {data['homework_name']} failed: {e}")
            self.conn.rollback()
        return False
    
    def update(self, sql, data, retries=3):
        for _ in range(retries):
            try:
                self.cur.execute(sql, data)
                self.conn.commit()
            except psycopg2.IntegrityError:
                print("Update failed due to integrity error")
                self.reconnect()

    def __del__(self):
        self.cur.close()
        self.conn.close()

