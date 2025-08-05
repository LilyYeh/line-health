# user_repo.py
# 此模組負責封裝對 db_context.py 的 SQLite 操作，提供更高階的資料存取介面。
# 所有註解皆為繁體中文。
from datetime import datetime

import calculate
import user
from db_context import DbContext

class UserRepo:
    """
    使用者資料存取層，負責呼叫 DbContext 進行 CRUD 操作。
    """
    def __init__(self):
        self.db = DbContext()

    # -------- user 資料表 --------
    def get_user_by_userid(self, userid):
        """
        依據 userid 取得單一使用者資料。
        """
        return self.db.get_user_by_userid(userid)

    def create_user(self, data, userid):
        """
        新增一筆使用者資料。
        """
        return self.db.create_user(data, userid)

    def update_user(self, userid, data):
        """
        更新指定 userid 的使用者資料。
        """
        return self.db.update_user(userid, data)

    # -------- health_record 資料表 --------
    def get_health_records_by_userid(self, userid):
        """
        依據 userid 取得所有健康紀錄。
        """
        return self.db.get_health_records_by_userid(userid)

    def create_health_record(self, data):
        """
        新增一筆健康紀錄。
        """
        return self.db.create_health_record(data)

    # -------- diet_record 資料表 --------
    def get_diet_records_by_userid(self, userid):
        """
        依據 userid 取得所有飲食紀錄。
        """
        return self.db.get_diet_records_by_userid(userid)

    def create_diet_record(self, data):
        """
        新增一筆飲食紀錄。
        """
        return self.db.create_diet_record(data)

    def get_all_record(self,userid):
        basic_inform = self.get_user_by_userid(userid)
        health_record = self.get_health_records_by_userid(userid)
        record_date = health_record['紀錄日期'] if len(health_record) != 0 else datetime.today().date().isoformat()
        diet_record = self.get_diet_records_by_userid(userid )

        record = basic_inform
        record['年齡'] = calculate.calculate_age(record['生日'])
        if health_record is not None:
            record.update(health_record)

        record['BMI'] = calculate.calculate_bmi(record['體重'], record['身高'])

        bmi = calculate.calculate_bmi(record['體重'], record['身高'])
        record['calorie'] = calculate.calculate_daily_calories(record['體重'], record['身高'], record['年齡'],
                                                               record['性別'])
        record['water'] = calculate.calculate_daily_water_intake(record['體重'])
        record['bmicate'] = calculate.classify_bmi(bmi)
        record[
            '建議'] = f"您的BMI為 {bmi}，屬於體型{record['bmicate']}族群。\n建議每天攝取熱量 {record['calorie']} 大卡，以及至少喝 {record['water']}ml 的水。"

        if diet_record is not None:
            record.update(diet_record)

        return record
    def close(self):
        """
        關閉資料庫連線。
        """
        self.db.close()

