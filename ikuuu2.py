#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2025/7/22 13:23
# -------------------------------
# cron "30 5 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('IKuuu机场签到帐号版')

import os
import requests
import json

# 从环境变量读取账号信息
ACCOUNT_STR = os.getenv('ikuuu', '')  # 格式：账号1&密码1#账号2&密码2

# 解析账号信息
ACCOUNTS = []
if ACCOUNT_STR:
    account_pairs = ACCOUNT_STR.split('#')
    for pair in account_pairs:
        if '&' in pair:
            email, password = pair.split('&', 1)  # 只分割第一个&符号
            ACCOUNTS.append({"email": email, "password": password})

if not ACCOUNTS:
    print("未检测到账号信息，请设置环境变量 ikuuu")
    print('格式示例：export ikuuu="账号1&密码1#账号2&密码2"')
    exit()

LOGIN_URL = "https://ikuuu.one/auth/login"
CHECKIN_URL = "https://ikuuu.one/user/checkin"

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}


def login_and_checkin(account):
    """处理单个账号的登录和签到"""
    session = requests.Session()

    # 登录请求
    login_data = {
        "host": "ikuuu.one",
        "email": account["email"],
        "passwd": account["password"],
        "code": ""
    }

    print(f"\n正在处理账号: {email}")
    try:
        login_response = session.post(LOGIN_URL, data=login_data, headers=COMMON_HEADERS)
        print(json.loads(login_response.text))
        if login_response.status_code != 200:
            print(f"登录失败! 状态码: {login_response.status_code}")
            return False

        # 签到请求
        checkin_response = session.post(CHECKIN_URL, headers=COMMON_HEADERS)

        if checkin_response.status_code == 200:
            response_data = json.loads(checkin_response.text)
            print(f"签到结果: {response_data.get('msg', '无返回消息')}")
            return True
        else:
            print(f"签到失败! 状态码: {checkin_response.status_code}")
            return False

    except Exception as e:
        print(f"处理账号 {email} 时出错: {str(e)}")
        return False


if __name__ == "__main__":
    print(f"检测到 {len(ACCOUNTS)} 个账号，开始签到...")

    success_count = 0
    for account in ACCOUNTS:
        if login_and_checkin(account):
            success_count += 1

    print(f"\n签到完成! 成功处理 {success_count}/{len(ACCOUNTS)} 个账号")
