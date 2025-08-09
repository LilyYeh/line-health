from openai import OpenAI, APIStatusError

import const
import handle_message
import user_repo

# chatGPT api
OPEN_AI_TOKEN = const.OPENAI_API_KEY

client = OpenAI(api_key=OPEN_AI_TOKEN)

def chatgpt_basic(Q):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system", "content":"以下對話請用繁體中文回答問題"},
            {"role":"user","content":""+Q+""}
        ]
    )
    # 返回答案
    return response.choices[0].message.content.strip()

#讓gpt計算每筆紀錄的熱量，並將熱量值存入資料表中
def chatgpt_calorie(diet_text):
    format = "- Subway 雞肉淺艇堡：約 400 大卡\n"
    format += "- 草莓蛋糕：約 250 大卡\n"
    format += "總熱量：約 550 大卡\n"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
            {"role":"system", "content":"以下對話請用繁體中文回答問題"},
            {"role":"user", "content": f"請幫我計算「{diet_text}」的熱量，回傳格式如：{format}。只需回傳格式內容，不需要其餘文字"}
        ]
    )

    return response.choices[0].message.content.strip()

# 處理圖片
def chatgpt_image(image_url: str = None):
    user_content = [
        {
            "type": "text",
            "text": """請先判斷照片是否為食物，若不是為食物請回應"請提供你吃的食物照片給我，我幫你計算熱量"，若為食物，請提供該食物的熱量及營養指標，並給予營養建議，並用繁體中文回答。"""
        },
        {
            "type": "image_url",
            "image_url": {"url": image_url}
        }
    ]

    messages = [
        {"role": "system", "content": "以下對話請用繁體中文回答問題"},
        {"role": "user", "content": user_content},
    ]

    try:
        response = client.chat.completions.create(
            model = "gpt-4o",
            messages=messages,
            max_tokens = 1000
        )
        return response.choices[0].message.content.strip()
    except APIStatusError as e:
        print(f"OpenAI API 錯誤: {e}")
        return f"發生錯誤: {e}"
    except Exception as e:
        print(f"發生未知錯誤: {e}")
        return f"發生未知錯誤: {e}"

def chatgpt_detect_info_type(text):
    messages = [
        {"role": "system", "content": "以下對話請用繁體中文回答問題，只回傳格式化後的訊息即可"},
        {"role": "user",
         "content": f"幫我判斷使用者訊息如下：{text}。若訊息只含有「性別、生日、身高、體重、目標」數值或文字等，則回傳一單字'basic'; 若訊息只含有「體重、喝水量、運動等級」等數值或文字，則回傳一單字'health'; 若訊息只含有「食物名稱、料理名稱」等文字，則回傳一單字'diet'。若含有其他資訊或提問，則回傳一個字'false'"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def chatgpt_format_basic_profile(basic_profile_text):
    format = "性別：女\n"
    format += "生日：1999-09-06\n"
    format += "身高：160\n"
    format += "體重：60\n"
    format += "目標：增肌\n"

    messages = [
        {"role": "system", "content": "以下對話請用繁體中文回答問題，只回傳格式化後的訊息即可"},
        {"role": "user",
         "content": f"請先幫我判斷{basic_profile_text}是否含有「性別、生日、身高、體重、目標」等數值，" +
                    f"回傳範例如下所述：若缺少'生日'，則回傳'請確認「生日」是否正確填寫'; 若缺少 '生日' '身高'，則回傳'請確認「生日、身高」是否正確填寫'; 以此類推。" +
                    f"若無缺值，請幫我格式化，格式化範例如：{format}。"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def chatgpt_format_health_record(health_record):
    format = "體重：50\n"
    format += "喝水量：2000\n"
    format += "運動等級：2\n"

    messages = [
        {"role": "system", "content": "以下對話請用繁體中文回答問題，只回傳格式化後的訊息即可"},
        {"role": "user",
         "content": f"請幫我格式化使用者的文字訊息，格式化範例如：{format}。使用者的文字訊息如下：{health_record}。只需回傳格式化後的文字即可。若文字訊息不含「體重、喝水量、運動等級」等數值或文字，則回傳一個字'false'"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def chatgpt_format_diet_record(diet_record):
    format = "水餃10顆\n"
    format += "雞胸肉1份\n"
    format += "火腿蛋餅1份\n"

    messages = [
        {"role": "system", "content": "以下對話請用繁體中文回答問題，只回傳格式化後的訊息即可"},
        {"role": "user",
         "content": f"請先幫我判斷此文字訊息是否只含「食物名稱、料理名稱」等文字，若有食物以外的文字，則回傳一個字'false'; 若只含「食物名稱、料理名稱」等文字，請幫我格式化此文字：{diet_record}，格式化範例如：{format}。"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def chatgpt_health_suggetion(userid):
    repo = user_repo.UserRepo()
    record = handle_message.dict_to_text(repo.get_all_record(userid))
    messages = [
        {"role": "system", "content": "你是一位營養師，同時也是一位健身教練，你會依照一個人的「性別、年齡、年齡、身高、體重、目標、飲食、喝水量、運動強度」，給我飲食與運動建議。請用繁體中文回答，回答請在 100 字以內。"},
        {"role": "user",
         "content": f"請依據以下資料來進行分析並給出飲食與運動建議:\n{record}"}
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def chatgpt_normal_question_reply(Q):
    messages = [
        {"role": "system",
         "content": "你是一位營養師，同時也是一位健身教練，你會回答我健康飲食和運動健身等專業的問題。請用繁體中文回答，回答請在 100 字以內。"},
        {"role": "user",
         "content": f"{Q}"}
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()
