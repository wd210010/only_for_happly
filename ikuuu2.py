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
from bs4 import BeautifulSoup

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

# HTML 内容（实际中可能通过请求获取）
HTML_CONTENT = requests.get("https://ikuuu.club/").text

def get_latest_domain(html_content):
    """从 HTML 中提取最新的活跃域名"""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        # 确保是活跃的域名（排除注释中的域名）
        if href.startswith('https://ikuuu.') and link.parent.text.strip() == href:
            return href.rstrip('/')
    return None

# 获取最新域名
DOMAIN = get_latest_domain(HTML_CONTENT)
if not DOMAIN:
    print("无法获取最新域名!")
    exit()

# 更新 URLs
LOGIN_URL = f"{DOMAIN}/auth/login"
CHECKIN_URL = f"{DOMAIN}/user/checkin"

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

def login_and_checkin(account):
    """处理单个账号的登录和签到"""
    session = requests.Session()

    # 登录请求
    login_data = {
        "host": DOMAIN.replace('https://', ''),
        "email": account["email"],
        "passwd": account["password"],
        "code": ""
    }

    print(f"\n正在处理账号: {account['email']}，使用域名: {DOMAIN}")
    try:
        login_response = session.post(LOGIN_URL, data=login_data, headers=COMMON_HEADERS)
        print(json.loads(login_response.text)['msg'])
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
        print(f"处理账号 {account['email']} 时出错: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"检测到 {len(ACCOUNTS)} 个账号，开始签到...")

    success_count = 0
    for account in ACCOUNTS:
        if login_and_checkin(account):
            success_count += 1

    print(f"\n签到完成! 成功处理 {success_count}/{len(ACCOUNTS)} 个账号")
