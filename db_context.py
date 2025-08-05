import sqlite3
from sqlite3 import Error

DB_FILE = 'user.db'

class DbContext:
    """
    此類別負責管理 SQLite 連線與三個資料表（user, health_record, diet_record）的 CRUD 操作。
    """
    def __init__(self):
        try:
            self.conn = sqlite3.connect(DB_FILE)
            self.create_user_table()
            self.create_health_record_table()
            self.create_diet_record_table()
        except Error as e:
            print(f"連線資料庫失敗: {e}")

    def create_user_table(self):
        """
        建立 user 資料表（若尚未存在）。
        """
        try:
            sql = '''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT NOT NULL,
                身高 Double,
                體重 Double,
                生日 TEXT,
                性別 TEXT,
                目標 TEXT,
                紀錄日期 TEXT
            )
            '''
            self.conn.execute(sql)
            self.conn.commit()
        except Error as e:
            print(f"建立 user 資料表失敗: {e}")

    def create_health_record_table(self):
        """
        建立 health_record 資料表（若尚未存在）。
        欄位：id, userid, 體重, 喝水量, 紀錄日期, 運動等級
        """
        try:
            sql = '''
            CREATE TABLE IF NOT EXISTS health_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT NOT NULL,
                體重 INTEGER,
                喝水量 INTEGER,
                紀錄日期 TEXT,
                運動等級 TEXT
            )
            '''
            self.conn.execute(sql)
            self.conn.commit()
        except Error as e:
            print(f"建立 health_record 資料表失敗: {e}")

    def create_diet_record_table(self):
        """
        建立 diet_record 資料表（若尚未存在）。
        欄位：id, 飲食內容, userid, 紀錄日期, 總熱量
        """
        try:
            sql = '''
            CREATE TABLE IF NOT EXISTS diet_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                飲食內容 TEXT,
                userid TEXT NOT NULL,
                紀錄日期 TEXT,
                總熱量 INTEGER
            )
            '''
            self.conn.execute(sql)
            self.conn.commit()
        except Error as e:
            print(f"建立 diet_record 資料表失敗: {e}")

    # user 資料表 CRUD
    def create_user(self, data, userid):
        try:
            sql = '''INSERT INTO user (userid, 身高, 體重, 生日, 性別, 目標, 紀錄日期) VALUES (?, ?, ?, ?, ?, ?, ?);'''
            cur = self.conn.cursor()
            cur.execute(sql, (
                userid,
                data.get('身高'),
                data.get('體重'),
                data.get('生日'),
                data.get('性別'),
                data.get('目標'),
                data.get('紀錄日期')
            ))
            self.conn.commit()
            return cur.lastrowid
        except Error as e:
            print(f"新增 user 失敗: {e}")
            return None

    def get_user_by_userid(self, userid):
        try:
            sql = 'SELECT * FROM user WHERE userid = ?;'
            cur = self.conn.cursor()
            cur.execute(sql, (userid,))
            row = cur.fetchone()
            if row:
                columns = [desc[0] for desc in cur.description]
                result = dict(zip(columns, row))
                result['table'] = 'user'
                return result
            return None
        except Error as e:
            print(f"查詢 user 失敗: {e}")
            return None

    def update_user(self, userid, data):
        try:
            sql = '''UPDATE user SET 身高=?, 體重=?, 生日=?, 性別=?, 目標=?, 紀錄日期=? WHERE userid=?;'''
            cur = self.conn.cursor()
            cur.execute(sql, (
                data.get('身高'),
                data.get('體重'),
                data.get('生日'),
                data.get('性別'),
                data.get('目標'),
                data.get('紀錄日期'),
                userid
            ))
            self.conn.commit()
            return cur.rowcount
        except Error as e:
            print(f"更新 user 失敗: {e}")
            return 0

    # health_record 資料表 CRUD
    def create_health_record(self, data):
        """
        新增一筆 health_record 資料。
        """
        try:
            sql = '''INSERT INTO health_record (userid, 體重, 喝水量, 紀錄日期, 運動等級) VALUES (?, ?, ?, ?, ?);'''
            cur = self.conn.cursor()
            cur.execute(sql, (
                data.get('userid'),
                data.get('體重'),
                data.get('喝水量'),
                data.get('紀錄日期'),
                data.get('運動等級')
            ))
            self.conn.commit()
            return cur.lastrowid
        except Error as e:
            print(f"新增 health_record 失敗: {e}")
            return None

    def get_health_records_by_userid(self, userid):
        try:
            sql = 'SELECT * FROM health_record WHERE userid = ?;'
            cur = self.conn.cursor()
            cur.execute(sql, (userid,))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            results = []
            for row in rows:
                record = dict(zip(columns, row))
                record['table'] = 'health_record'
                results.append(record)
            return results
        except Error as e:
            print(f"查詢 health_record 失敗: {e}")
            return []

    # diet_record 資料表 CRUD
    def create_diet_record(self, data):
        """
        新增一筆 diet_record 資料。
        """
        try:
            sql = '''INSERT INTO diet_record (飲食內容, userid, 紀錄日期, 總熱量) VALUES (?, ?, ?, ?);'''
            cur = self.conn.cursor()
            cur.execute(sql, (
                data.get('飲食內容'),
                data.get('userid'),
                data.get('紀錄日期'),
                data.get('總熱量')
            ))
            self.conn.commit()
            return cur.lastrowid
        except Error as e:
            print(f"新增 diet_record 失敗: {e}")
            return None

    def get_diet_records_by_userid(self, userid):
        try:
            sql = 'SELECT * FROM diet_record WHERE userid = ?;'
            cur = self.conn.cursor()
            cur.execute(sql, (userid,))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            results = []
            for row in rows:
                record = dict(zip(columns, row))
                record['table'] = 'diet_record'
                results.append(record)
            return results
        except Error as e:
            print(f"查詢 diet_record 失敗: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
