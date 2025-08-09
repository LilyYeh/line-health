from datetime import datetime
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, ButtonsTemplate, MessageAction
from linebot.models import RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds

import calculate
import const

#註冊基本資料
def get_first_login_text():
    return (
        "👋 歡迎使用健康助理 LINE Bot！\n\n"
        "請協助填寫以下基本資料 👇\n"
        "🔹性別（男/女）\n"
        "🔹生日（yyyy-mm-dd）\n"
        "🔹身高（cm）\n"
        "🔹體重（kg）\n"
        "🔹目標（減脂、增肌、維持體重、提升健康）\n\n"
        "📌 請依照上述格式一次輸入，謝謝！"
    )

#記錄健康範例
def get_record_health_text():
    return (
        "📝 請協助填寫以下健康資訊 👇\n"
        "🔹體重（kg）\n"
        "🔹喝水量（ml）\n"
        "🔹運動等級（1~5）\n\n"
        "運動等級說明\n"
        " • 運動等級1：日常走路（如通勤、逛街）\n"
        " • 運動等級2：健走 / 快走\n"
        " • 運動等級3：慢跑 / 跑步（持續流汗、喘氣）\n"
        " • 運動等級4：重訓、有氧交叉訓練、高強度間歇運動（HIIT）\n"
        " • 運動等級5：勞力工作者 / 運動員訓練 \n"
    )

#記錄飲食範例
def get_record_diet_text():
    return (
        "📝 請協助填寫飲食資訊 👇\n"
        "🔹輸入範例：水餃10顆 雞胸肉1份\n"
    )

# 功能選單
def get_main_menu():
    return TemplateSendMessage(
        alt_text='AI健康助理',
        template=ButtonsTemplate(
            title='請選擇功能',
            text='請選擇以下功能，或上傳美食圖片，健康助理將為您提供飲食建議。',
            actions=[
                MessageAction(
                    label='查閱健康紀錄',
                    text='查閱健康紀錄'
                ),
                MessageAction(
                    label='記錄飲食',
                    text='記錄飲食'
                ),
                MessageAction(
                    label='記錄健康',
                    text='記錄健康'
                ),
                MessageAction(
                    label='飲食&運動建議',
                    text='飲食&運動建議'
                ),
            ]
        )
    )

# 功能選單(圖文選單)
def set_line_main_menu():
    img_path = const.RICH_MENU
    line_bot_api = LineBotApi(const.LINE_CHANNEL_ACCESS_TOKEN)
    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=2500, height=843),
        selected=True,
        name="健康管理選單",
        chat_bar_text="健康選單",
        areas=[
            RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=625, height=843),
                         action=MessageAction(label='查閱健康紀錄', text='查閱健康紀錄')),
            RichMenuArea(bounds=RichMenuBounds(x=625, y=0, width=625, height=843),
                         action=MessageAction(label='記錄飲食', text='記錄飲食')),
            RichMenuArea(bounds=RichMenuBounds(x=1250, y=0, width=625, height=843),
                         action=MessageAction(label='記錄健康', text='記錄健康')),
            RichMenuArea(bounds=RichMenuBounds(x=1875, y=0, width=625, height=843),
                         action=MessageAction(label='飲食&運動建議', text='飲食&運動建議'))
        ]
    )

    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
    print("建立成功，Rich Menu ID:", rich_menu_id)

    with open(img_path, 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg", f)

    line_bot_api.set_default_rich_menu(rich_menu_id)
    print("已設定為預設選單")

def basic_record_description(record):
    age = calculate.calculate_age(record['生日'])
    height = record['身高']
    weight = record['體重']
    gender = record['性別']
    bmi = calculate.calculate_bmi(weight, height)
    calorie = calculate.calculate_daily_calories(weight, height, age, gender)
    water = calculate.calculate_daily_water_intake(weight)
    bmicate = calculate.classify_bmi(bmi)
    result_reply = f"✅ 已成功建立您的基本資料。\n\n"
    result_reply += f"📊 您的BMI為 {bmi}，屬於體型{bmicate}族群。\n\n"
    result_reply += f"📌 建議每天攝取熱量 {calorie} 大卡，以及至少喝 {water}ml 的水。"
    result_gpt = f"你是一位營養師 請根據bmi{bmi}，年齡{age}，性別{gender}這些資訊，提供約50字內的健康風險評估與改善建議"
    return result_reply, result_gpt

def dict_to_text(dict):
    text = ""
    for key, value in dict.items():
        text += f"{key}: {value}\n"
    return text

def line_flex_template(record):
    flex_message_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "健康紀錄",
                    "weight": "bold",
                    "size": "xl",
                    "margin": "md",
                    "color": "#1DB446"
                },
                {
                    "type": "text",
                    "text": f"紀錄日期: {record['紀錄日期'] if '紀錄日期' in record else datetime.today().date().isoformat()}",
                    "size": "sm",
                    "color": "#666666"
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"性別: {record['性別']}",
                            "size": "sm",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": f"年齡: {record['年齡']}",
                            "size": "sm",
                            "flex": 1
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"身高: {record['身高']} cm",
                            "size": "sm",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": f"體重: {record['體重']} kg",
                            "size": "sm",
                            "flex": 1
                        }
                    ]
                },
            ]
        }
    }

    # 健康紀錄
    health_record_content = []
    if '運動等級' in record:
        health_record_content.append({
            "type": "text",
            "text": f"運動等級: {record['運動等級']}",
            "size": "sm",
            "flex": 1
        })
    if '喝水量' in record:
        health_record_content.append({
            "type": "text",
            "text": f"喝水量: {record['喝水量']} ml",
            "size": "sm",
            "flex": 1
        })

    if len(health_record_content) > 0:
        flex_message_json['body']['contents'].extend([
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": health_record_content
            }
        ])

    # BMI
    flex_message_json['body']['contents'].extend([
        {
            "type": "separator",
            "margin": "lg"
        },
        {
            "type": "text",
            "text": f"BMI: {record['BMI']} ({record['bmicate']})",
            "margin": "lg",
            "size": "md",
            "weight": "bold"
        },
        {
            "type": "box",
            "layout": "vertical",
            "margin": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": f"{record['建議']}",
                    "wrap": True,
                    "size": "sm",
                    "color": "#666666"
                }
            ]
        },
    ])

    # 飲食記錄
    diet_record_content = []
    if '總熱量' in record:
        lines = [line.strip() for line in record['總熱量'].split('\n')]
        for i, line in enumerate(lines):
            content_item = {
                "type": "text",
                "text": line,
                "size": "sm",
                "weight": "bold" if "總熱量" in line else "regular",  # 總熱量加粗
                "color": "#1DB446" if "總熱量" in line else "#000000"  # 總熱量上色
            }
            diet_record_content.append(content_item)

    if len(diet_record_content) > 0:
        flex_message_json['body']['contents'].extend([
            {
                "type": "separator",
                "margin": "lg"
            },
            {
                "type": "text",
                "text": "飲食內容與熱量",
                "margin": "lg",
                "size": "md",
                "weight": "bold"
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "md",
                "contents": diet_record_content
            }
        ])

    return flex_message_json
