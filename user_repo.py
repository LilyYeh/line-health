from datetime import datetime
import calculate
import chat_gpt
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
    def get_health_records_by_userid(self, userid, record_date):
        """
        依據 userid 取得所有健康紀錄。
        """
        return self.db.get_health_records_by_userid(userid, record_date)

    def create_health_record(self, data):
        """
        新增一筆健康紀錄。
        """
        return self.db.create_health_record(data)

    def update_health_record(self, userid, record_date, data):
        """
        更新指定 userid 的使用者資料。
        """
        return self.db.update_health_record(userid, record_date, data)

    # -------- diet_record 資料表 --------
    def get_diet_records_by_userid(self, userid, record_date):
        """
        依據 userid 取得所有飲食紀錄。
        """
        return self.db.get_diet_records_by_userid(userid, record_date)

    def create_diet_record(self, data):
        """
        新增一筆飲食紀錄。
        """
        return self.db.create_diet_record(data)

    def get_all_record(self,userid):
        record_date = datetime.today().strftime('%Y-%m-%d')
        basic_inform = self.get_user_by_userid(userid)
        health_record = self.get_health_records_by_userid(userid, record_date)
        diet_records = self.get_diet_records_by_userid(userid, record_date)

        record = basic_inform
        record['紀錄日期'] = record_date
        record['年齡'] = calculate.calculate_age(record['生日'])

        if health_record is not None:
            record['紀錄日期'] = health_record['紀錄日期']
            record['體重'] = health_record['體重']
            record['喝水量'] = health_record['喝水量']
            record['運動等級'] = health_record['運動等級']

        record['BMI'] = bmi = calculate.calculate_bmi(record['體重'], record['身高'])
        record['calorie'] = calculate.calculate_daily_calories(record['體重'], record['身高'], record['年齡'], record['性別'])
        record['water'] = calculate.calculate_daily_water_intake(record['體重'])
        record['bmicate'] = calculate.classify_bmi(bmi)
        record['建議'] = f"您的BMI為 {bmi}，屬於體型{record['bmicate']}族群。\n建議每天攝取熱量 {record['calorie']} 大卡，以及至少喝 {record['water']}ml 的水。"

        if diet_records is not None:
            diet_records_text = "、".join(item['飲食內容'] for item in diet_records)
            chatgpt_response = chat_gpt.chatgpt_calorie(diet_records_text)
            record['總熱量'] = chatgpt_response

        return record

    def convert_types(self,record_text):
        result_dict = {}
        lines = record_text.strip().split('\n')
        for line in lines:
            parts = line.rstrip().split('：', 1)

            if len(parts) == 2:
                key = parts[0].strip()
                value_str = parts[1].strip()

                if key == '生日':
                    try:
                        result_dict[key] = datetime.strptime(value_str, '%Y-%m-%d').date().isoformat()
                    except ValueError:
                        result_dict[key] = value_str
                elif key in ['身高', '體重']:
                    try:
                        result_dict[key] = float(value_str)
                    except ValueError:
                        result_dict[key] = value_str
                else:
                    result_dict[key] = value_str

        return result_dict

    def close(self):
        """
        關閉資料庫連線。
        """
        self.db.close()

