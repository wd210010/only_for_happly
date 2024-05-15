import json
import pprint
import requests
import re
import os
import random
import time
from urllib.parse import urlparse, parse_qs
from notify import send

# 定义常量
API_URL = "https://api.weibo.cn/2/cardlist"
SIGN_URL = "https://api.weibo.cn/2/page/button"


# 请求接口
def send_request(url, params, headers):
    max_retries = 15  # 设置最大尝试次数
    wait_time = 5  # 设置每次尝试之间的等待时间（秒）
    response = requests.get(url, params=params, headers=headers)
    for i in range(max_retries):
        try:
            if 200 <= response.status_code < 300:
                # 请求成功，退出循环
                break
            else:
                # 如果服务器响应不是2xx，我们也认为是请求失败
                raise requests.RequestException(f"HTTP Error: {response.status_code}")
        except requests.RequestException as e:
            if i < max_retries - 1:
                print(f"请求失败，原因: {e}。{wait_time}秒后重试...")
                time.sleep(wait_time)
                continue
            else:
                raise

    data = json.loads(response.text)

    return data


# 提取cookie中的gsid
def generate_authorization(cookie):
    gsid = cookie.get("gsid")
    if gsid is not None:
        return f"WB-SUT {gsid}"
    else:
        return None


def extract_params(url):
    # 解析URL
    parsed_url = urlparse(url)

    # 提取查询参数
    params_from_cookie = parse_qs(parsed_url.query)

    # 将列表值转换为单个值
    params_from_cookie = {k: v[0] for k, v in params_from_cookie.items()}

    return params_from_cookie


# 获取get_since_id
def get_since_id(params, headers):
    data = send_request(API_URL, params, headers)
    since_id = data["cardlistInfo"]["since_id"]
    return since_id


# 获取超话列表
def get_topics(params, headers):
    data = send_request(API_URL, params, headers)
    cards = data.get("cards", [])
    topics = []
    for card in cards:
        if card.get("card_type") == "11":
            card_group = card.get("card_group", [])
            for item in card_group:
                if item.get("card_type") == "8":
                    sign_action = None
                    if "buttons" in item and len(item["buttons"]) > 0:
                        button = item["buttons"][0]
                        if "params" in button and "action" in button["params"]:
                            sign_action = button["params"]["action"]

                    topic = {
                        "title": item.get("title_sub"),
                        "desc": item.get("desc1"),
                        "sign_status": item.get("buttons", [{}])[0].get("name", ""),
                        "sign_action": sign_action
                        if item.get("buttons", [{}])[0].get("name", "") != "已签"
                        else "",
                    }

                    topics.append(topic)
    output = ""
    for topic in topics:
        output += "超话标题:'{}'，状态:'{}'\n".format(topic["title"], topic["sign_status"])

    print(output)
    return topics


# 超话签到
def sign_topic(title, action, params, headers):
    message = ""
    action = re.search(r"request_url=(.+)", action).group(1)
    params["request_url"] = action
    time.sleep(random.randint(5, 10))  # 暂停执行wait_time秒
    resp = requests.get(SIGN_URL, params=params, headers=headers)
    # print('服务器返回信息:', resp.json())
    if resp.json().get("msg") == "已签到":
        qd_output = "超话标题:'{}'，状态:'签到成功！'\n".format(title)
        print(qd_output)
        message += qd_output

    else:
        print("签到失败!")

    return message


def get_username(params, headers):
    url = 'https://api.weibo.cn/2/profile/me'
    response = requests.get(url, headers=headers, params=params)
    data = json.loads(response.text)
    return data['mineinfo']['screen_name']


headers = {
    "Accept": "*/*",
    "User-Agent": "Weibo/81434 (iPhone; iOS 17.0; Scale/3.00)",
    "SNRT": "normal",
    "X-Sessionid": "6AFD786D-9CFA-4E18-BD76-60D349FA8CA2",
    "Accept-Encoding": "gzip, deflate",
    "X-Validator": "QTDSOvGXzA4i8qLXMKcdkqPsamS5Ax1wCJ42jfIPrNA=",
    "Host": "api.weibo.cn",
    "x-engine-type": "cronet-98.0.4758.87",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en",
    "cronet_rid": "6524001",
    "Authorization": "",
    "X-Log-Uid": "5036635027",
}

if __name__ == "__main__":
    succeeded = False
    # 获取参数
    # weibo_my_cookie = ''
    params = extract_params(os.getenv("weibo_my_cookie"))
    # params = extract_params(weibo_my_cookie)
    message_to_push = ""
    while not succeeded:
        try:

            # 获取用户名
            name = get_username(params, headers)
            print('用户名:', name + '\n')
            since_id = get_since_id(params, headers)
            params["count"] = "1000"
            # 更新header参数
            headers["Authorization"] = generate_authorization(params)

            # 外部循环，用于重新获取并处理主题，直到所有主题的 sign_action 都为空
            while True:
                # 重置 output 为空字符串
                output = ""
                # 假设您有一个函数 get_topics 来获取主题列表
                topics = get_topics(params, headers)
                # 检查是否存在 sign_action 不为空的主题
                has_sign_action = any(
                    topic.get("sign_action") != "" for topic in topics
                )
                # 如果没有 sign_action 不为空的主题，则退出外部循环
                if not has_sign_action:
                    break
                # 原始的外部循环，用于格式化输出
                for topic in topics:
                    output += "超话标题:'{}'，状态:'{}'\\n".format(
                        topic["title"], topic["sign_status"]
                    )
                # 原始的内部循环，用于检查和处理 sign_action
                for topic in topics:
                    if topic.get("sign_action") != "":
                        action = topic.get("sign_action")
                        title = topic.get("title")
                        message = sign_topic(title, action, params, headers)
                        message_to_push += message  # 将每个主题的消息追加到最终要推送的消息中

                # print(output)

            succeeded = True
        except Exception as e:
            print(e)
            time.sleep(60)

    # print('message:', message)
    send("微博签到结果:", message_to_push)
