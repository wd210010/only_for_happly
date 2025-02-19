import json
from datetime import datetime

# 获取当前日期
current_date = datetime.now().strftime('%Y-%m-%d')

# 定义 JSON 文件路径
json_file = 'date_config.json'

# 更新 JSON 文件
def update_json():
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # 更新日期字段
    data['date'] = current_date

    # 写回更新后的内容
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    update_json()
