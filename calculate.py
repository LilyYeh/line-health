from datetime import datetime, date
import re

#計算BMI/熱量/每日飲水量/是否為肥胖族群
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def calculate_daily_calories(weight_kg, height_cm, age, gender, activity_factor=1.2):
    # gender: "男" or "女"
    if gender == '男':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    elif gender == '女':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age  # 無性別假設

    return round(bmr * activity_factor)

def calculate_daily_water_intake(weight_kg):
    water_min = weight_kg * 30
    return (int(water_min))

def classify_bmi(bmi):
    if bmi < 18.5:
        return "過輕"
    elif 18.5 <= bmi <= 23.9:
        return "正常"
    elif 24.0 <= bmi <= 26.9:
        return "過重"
    elif 27.0 <= bmi <= 29.9:
        return "輕度肥胖"
    elif 30.0 <= bmi <= 34.9:
        return "中度肥胖"
    else:
        return "重度肥胖"

def calculate_age(birthdate_str):
    # 解析出生日期（格式為 YYYY-MM-DD）
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
    today = date.today()

    # 計算年齡
    age = today.year - birthdate.year
    # 如果還沒過生日，就減一歲
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1

    return age

def chinese_char_count(text):
    # 用正則表達式找出所有中文字符（Unicode 範圍）
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars)
def total_calories(diet_records):
    """
    計算飲食紀錄中的總熱量。
    :param diet_records:
    :return:總熱量數字
    """
    total = 0
    for record in diet_records:
        try:
            # 從描述中擷取大卡前的數字
            match = re.search(r'(\d+)\s*大卡', record)
            if match:
                total += int(match.group(1))
        except ValueError:
            continue  # 如果轉換失敗，則跳過該紀錄
    return total if total > 0 else None
def total_water_intake(diet_records):
    """
    總喝水量計算
    :param diet_records:
    :return:
    """
    total = 0
    for record in diet_records:
        try:
            # 從描述中擷取水量前的數字
                total += int(record)
        except ValueError:
            continue  # 如果轉換失敗，則跳過該紀錄
    return total if total > 0 else None
