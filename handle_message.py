from datetime import datetime
from linebot.models import TemplateSendMessage, ButtonsTemplate,MessageAction

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

def dict_to_text(dict):
    text = ""
    for key, value in dict.items():
        text += f"{key}: {value}\n"
    return text

def line_flex_template(record):
    contents = []
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
            contents.append(content_item)

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

    if '運動等級' in record or '喝水量' in record:
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

        flex_message_json['body']['contents'].extend([
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": health_record_content
            }
        ])


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

    if len(contents) > 0:
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
                "contents": contents  # 直接將內容列表放進來
            }
        ])

    return flex_message_json
