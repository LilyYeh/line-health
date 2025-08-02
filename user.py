import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import re
import pandas as pd
from datetime import datetime
import calculate
import chat_gpt
import const

shared_link = const.GOOGLE_SHEET_LINK
gc = gspread.service_account(filename=const.SERVICE_ACCOUNT_FILE)

basicinform_sheet = gc.open_by_url(shared_link).worksheet("basicinform")
healthrecord_sheet = gc.open_by_url(shared_link).worksheet("healthrecord")
dietrecord_sheet = gc.open_by_url(shared_link).worksheet("dietrecord")

basicin_column = basicinform_sheet.get_all_values()[0]
healthre_column = healthrecord_sheet.get_all_values()[0]
dietrecord_column = dietrecord_sheet.get_all_values()[0]

bi_df = pd.DataFrame(basicinform_sheet.get_all_values()[1:], columns=basicin_column)
hr_df = pd.DataFrame(healthrecord_sheet.get_all_values()[1:], columns=healthre_column)
dr_df = pd.DataFrame(dietrecord_sheet.get_all_values()[1:], columns=dietrecord_column)

# 利用 userid 來判斷該用戶是否為第一次使用
def detect_message_type(userid0):
    id_identify_list = list(get_as_dataframe(basicinform_sheet).dropna(how='all').userid.unique())
    if userid0 in id_identify_list:
        return 'logging'
    else:
        id_identify_list.append(userid0)
    return 'registering'


# 紀錄使用者輸入的基本資訊 並回傳到googlesheet
def basic_record_save(data, userid):
    sheet_columns = ['userid', '身高', '體重', '生日', '性別', '目標', '紀錄日期']

    data['userid'] = userid
    data['紀錄日期'] = datetime.today().date().isoformat()

    my_bi_df = pd.DataFrame([data])
    if userid in bi_df['userid'].values:
        idx_to_update = bi_df[bi_df['userid'] == userid].index[0]
        for col in my_bi_df.columns:
            bi_df.loc[idx_to_update, col] = my_bi_df.loc[0, col]
        new_bi_df = bi_df[sheet_columns]
        set_with_dataframe(basicinform_sheet, new_bi_df)
    else:
        new_record_values = []
        for col in sheet_columns:
            value = data.get(col, '')
            if pd.isna(value):
                new_record_values.append('')
            else:
                new_record_values.append(value)
        basicinform_sheet.append_row(new_record_values)

# 根據輸入的基本資訊回傳簡短統計資訊(result_reply)，並生成讓gpt回復的prompt(result_gpt)
def basic_record_description(record):
    #today = datetime.today()
    #age = today.year - record['生日'].year - ((today.month, today.day) < (record['生日'].month, record['生日'].day))
    age = calculate.calculate_age(record['生日'])
    height = record['身高']
    weight = record['體重']
    gender = record['性別']
    bmi = calculate.calculate_bmi(weight, height)
    calorie = calculate.calculate_daily_calories(weight, height, age, gender)
    water = calculate.calculate_daily_water_intake(weight)
    bmicate = calculate.classify_bmi(bmi)
    result_reply = f"✅ 已成功建立您的基本資料。\n\n"
    result_reply += f"📊 您的BMI為 {bmi}，屬於體型{bmicate}族群。\n📌建議每天攝取熱量 {calorie} 大卡，以及至少喝 {water}ml 的水。"
    result_gpt = f"你是一位營養師 請根據bmi{bmi}，年齡{age}，性別{gender}這些資訊，提供約50字內的健康風險評估與改善建議"
    return result_reply, result_gpt


def convert_types(record_text):
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

#儲存使用者輸入的健康資訊 並回傳確認訊息
def health_record_save_and_reply(data,userid):
  sheet_columns = ['userid', '體重', '喝水量', '紀錄日期', '運動等級']

  today = datetime.today().date().isoformat()
  data['userid'] = userid
  data['紀錄日期'] = today
  my_hr_df = pd.DataFrame([data])

  idx_to_update = hr_df[(hr_df['userid'] == userid) & (hr_df['紀錄日期'] == today)].index
  if not idx_to_update.empty:
      print('update data')
      for col in my_hr_df.columns:
          hr_df.loc[idx_to_update[0], col] = my_hr_df.loc[0, col]
      new_hr_df = hr_df
      set_with_dataframe(healthrecord_sheet, new_hr_df)
  else:
      print('insert data')
      new_record_values = []
      for col in sheet_columns:
          value = data.get(col, '')
          if pd.isna(value):
              new_record_values.append('')
          else:
              new_record_values.append(value)
      healthrecord_sheet.append_row(new_record_values)

  reply_text=f"✅ 健康紀錄完成！已儲存 {today} 最新數據。"
  return reply_text

#讀取使用者的飲食紀錄
def diet_record_data(input):
  cleaned_input = re.sub(r"[\n\/\-\.,;；、]", " ", input).strip()
  return {"飲食內容":cleaned_input.strip()}

#儲存使用者輸入的健康資訊 並回傳確認訊息
def diet_record_save_and_reply(data, userid):
  google_sheet_headers = ['飲食內容', 'userid', '紀錄日期']

  data['userid']=userid
  data['紀錄日期']=datetime.today().date()

  new_record_values = [data['飲食內容'], data['userid'], data['紀錄日期'].isoformat()]
  dietrecord_sheet.append_row(new_record_values)

  #回復訊息
  reply_text = f"✅ 飲食紀錄完成！"

  return reply_text

def get_basic_inform(userid):
    bi_df = get_as_dataframe(basicinform_sheet).dropna(how='all')
    bi_df_final = bi_df[bi_df['userid'] == userid]
    if bi_df_final.empty:
        return None

    data = bi_df_final.to_dict('records')[0]
    return {
        '性別': data['性別'],
        '年齡': calculate.calculate_age(data['生日']),
        '身高': data['身高'],
        '體重': data['體重'],
        '目標': data['目標'],
    }

def get_health_record(userid):
    hr_df = get_as_dataframe(healthrecord_sheet).dropna(how='all')
    hr_df_final = hr_df[hr_df['userid'] == userid]
    if hr_df_final.empty:
        return None

    hr_df_final['紀錄日期'] = pd.to_datetime(hr_df_final['紀錄日期'])
    hr_df_sorted = hr_df_final.sort_values(by=['userid', '紀錄日期'], ascending=[True, False])
    latest_records_df = hr_df_sorted.drop_duplicates(subset=['userid'], keep='first')

    data = latest_records_df.to_dict('records')[0]

    re = { '紀錄日期': data['紀錄日期'].strftime('%Y-%m-%d') }
    if not pd.isna(data['體重']):
        re['體重'] = data['體重']

    if not pd.isna(data['喝水量']):
        re['喝水量'] = data['喝水量']

    if not pd.isna(data['運動等級']):
        re['運動等級'] = data['運動等級']

    return re

def get_diet_record(userid, record_date):
    diet_df = get_as_dataframe(dietrecord_sheet).dropna(how='all')
    is_record_today = diet_df[(diet_df['userid'] == userid) & (diet_df['紀錄日期'] == record_date)].index

    if is_record_today.empty:
        return None

    diet_df_final = diet_df[diet_df['userid'] == userid]

    df_grouped = diet_df_final.groupby(['userid', '紀錄日期']).agg(
        飲食內容=('飲食內容', lambda x: '、'.join(x)),  # 將飲食內容用空格連接起來
    ).reset_index()

    df_grouped['紀錄日期'] = pd.to_datetime(df_grouped['紀錄日期'])
    diet_df_sorted = df_grouped.sort_values(by=['userid', '紀錄日期'], ascending=[True, False])

    latest_records_df = diet_df_sorted.drop_duplicates(subset=['userid'], keep='first')
    data = latest_records_df.to_dict('records')[0]

    chatgpt_response = chat_gpt.chatgpt_calorie(data['飲食內容'])

    return {
        #'飲食內容': data['飲食內容'],
        '總熱量': chatgpt_response
    }

def get_all_record(userid):
    basic_inform = get_basic_inform(userid)
    health_record = get_health_record(userid)
    record_date = health_record['紀錄日期'] if health_record is not None else datetime.today().date().isoformat()
    diet_record = get_diet_record(userid, record_date)

    record = basic_inform
    if health_record is not None:
        record.update(health_record)

    record['BMI'] = calculate.calculate_bmi(record['體重'], record['身高'])

    bmi = calculate.calculate_bmi(record['體重'], record['身高'])
    record['calorie'] = calculate.calculate_daily_calories(record['體重'], record['身高'], record['年齡'], record['性別'])
    record['water'] = calculate.calculate_daily_water_intake(record['體重'])
    record['bmicate'] = calculate.classify_bmi(bmi)
    record['建議'] = f"您的BMI為 {bmi}，屬於體型{record['bmicate']}族群。\n建議每天攝取熱量 {record['calorie']} 大卡，以及至少喝 {record['water']}ml 的水。"

    if diet_record is not None:
        record.update(diet_record)

    return record