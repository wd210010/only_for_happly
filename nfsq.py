import time
import os
import requests
from datetime import datetime
import json


#抓取农夫山泉抽水小程序 获取apitoken值填入环境变量 变量名字为nfsq
# Constants
API_BASE_URL = "https://gateway.jmhd8.com"
USER_INFO_URL = f"{API_BASE_URL}/geement.usercenter/api/v1/user/information"
TASK_LIST_URL = f"{API_BASE_URL}/geement.marketingplay/api/v1/task"
JOIN_TASK_URL = f"{API_BASE_URL}/geement.marketingplay/api/v1/task/join"
LOTTERY_URL = "https://thirtypro.jmhd8.com/api/v1/nongfuwater/snake/checkerboard/lottery"
MARKETING_LOTTERY_URL = f"{API_BASE_URL}/geement.marketinglottery/api/v1/marketinglottery"
SENIORITY_URL = f"{API_BASE_URL}/geement.usercenter/api/v1/user/seniority"
TODAY_COUNT_URL = f"{API_BASE_URL}/geement.actjextra/api/v1/act/lottery/data/todaycount"
GOODS_SIMPLE_URL = f"{API_BASE_URL}/geement.actjextra/api/v1/act/win/goods/simple"

# Headers
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c11)XWEB/11581",
    'content-type': "application/x-www-form-urlencoded",
    'xweb_xhr': "1",
    'unique_identity': "b78effb9-789e-416c-8e2b-84f7d9dadbb6",
    'sec-fetch-site': "cross-site",
    'sec-fetch-mode': "cors",
    'sec-fetch-dest': "empty",
    'referer': "https://servicewechat.com/wxd79ec05386a78727/86/page-frame.html",
    'accept-language': "zh-CN,zh;q=0.9"
}


def get_apitokens():
    tokenString = os.getenv("nfsq")
    if not tokenString:
        print('没有配置nfsq')
        exit()
    return tokenString.split("#")


def make_request(method, url, headers=None, params=None, json_data=None):
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=json_data)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None


def login(apitoken):
    headers = {**HEADERS, 'apitoken': apitoken}
    response = make_request('GET', USER_INFO_URL, headers=headers)
    if response and 'data' in response:
        data = response['data']
        return data['user_no'], data['nick_name']
    return None, None


def get_task_list(apitoken):
    headers = {**HEADERS, 'apitoken': apitoken}
    params = {'pageNum': '1', 'pageSize': '10', 'task_status': '2', 'status': '1', 'group_id': '24121016331837'}
    response = make_request('GET', TASK_LIST_URL, headers=headers, params=params)
    return response['data'] if response else []


def do_task(taskId, apitoken):
    headers = {**HEADERS, 'apitoken': apitoken}
    params = {'action_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'task_id': taskId}
    response = make_request('GET', JOIN_TASK_URL, headers=headers, params=params)
    print(response)


def lottery(apitoken):
    payload = {
        "code": "SCENE-24121018362724",
        "provice_name": "上海市",
        "city_name": "上海市",
        "area_name": "浦东新区",
        "address": "上海市浦东新区东方路121号",
        "longitude": 121.520630,
        "dimension": 31.239136
    }
    headers = {**HEADERS, 'apitoken': apitoken, 'Content-Type': "application/json"}
    response = make_request('POST', LOTTERY_URL, headers=headers, json_data=payload)
    return response


def marketing_lottery(apitoken, code):
    payload = {
        "code": code,
        "provice_name": "上海市",
        "city_name": "上海市",
        "area_name": "浦东新区",
        "address": "上海市浦东新区东方路121号",
        "longitude": 121.520630,
        "dimension": 31.239136
    }
    headers = {**HEADERS, 'apitoken': apitoken, 'Content-Type': "application/json"}
    response = make_request('POST', MARKETING_LOTTERY_URL, headers=headers, json_data=payload)
    if response and response['code'] == 500:
        print(response['msg'])
    elif response and 'data' in response:
        print(response['data']['prizedto']['prize_name'])


def today_count(apitoken):
    params = {'act_code': "ACT2412101428048"}
    headers = {**HEADERS, 'apitoken': apitoken}
    response = make_request('GET', TODAY_COUNT_URL, headers=headers, params=params)
    return response['data'] if response else 0


def goods_simple(apitoken):
    params = {'act_codes': "ACT2412101428048,ACT24121014352835,ACT24121014371732"}
    headers = {**HEADERS, 'apitoken': apitoken}
    response = make_request('GET', GOODS_SIMPLE_URL, headers=headers, params=params)
    return response['data'] if response else []


def process_account(apitoken):
    user_no, nick_name = login(apitoken)
    print(f"============账号nick_name:{nick_name or user_no}============")

    everydata_counted = today_count(apitoken)
    print("每日赠送抽奖", f"[{everydata_counted}/3]")

    if everydata_counted < 3:
        code = "SCENE-24121018345681"
        for _ in range(3 - everydata_counted):
            marketing_lottery(apitoken, code)
            time.sleep(1)

    task_list = get_task_list(apitoken)
    print("======执行任务======")
    for task in task_list:
        task_name = task["name"]
        task_status = task["complete_status"]
        task_id = task['id']
        allow_complete_count = task["allow_complete_count"]
        complete_count = task["complete_count"]

        if task_status == 1:
            print(f"{task_name} 已完成,跳过")
        else:
            print(f"开始 {task_name} [{complete_count}/{allow_complete_count}]")
            for _ in range(allow_complete_count - complete_count):
                do_task(task_id, apitoken)
                time.sleep(1)

    print("时来运转游戏")
    for _ in range(3):
        lottery_mes = lottery(apitoken)
        if lottery_mes and lottery_mes["success"] == False:
            print(lottery_mes['msg'])
            break
        else:
            print(lottery_mes['data'] if lottery_mes else "请求失败")
        time.sleep(1)

    print("======任务完成情况======")
    for task in task_list:
        task_name = task["name"]
        task_status = task["complete_status"]
        complete_count = task["complete_count"]
        allow_complete_count = task["allow_complete_count"]
        print(f"[{'√' if task_status == 1 else '×'}] {task_name} [{complete_count}/{allow_complete_count}]")

    print("======查询奖品======")
    goods_list = goods_simple(apitoken)
    for good in goods_list:
        if good.get("win_goods_sub_type"):
            print(good["win_goods_name"])


if __name__ == '__main__':
    apitoken_list = get_apitokens()
    for apitoken in apitoken_list:
        process_account(apitoken)
