import json
from datetime import datetime

# 获取今天的日期
today_date = datetime.today().strftime('%Y-%m-%d')

# 创建一个字典来存储日期信息
date_info = {
    'date': today_date
}

# 将日期数据保存到 JSON 文件中
with open('date.json', 'w') as f:
    json.dump(date_info, f, indent=4)

print("Date updated.")
