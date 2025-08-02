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
