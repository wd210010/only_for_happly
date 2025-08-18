#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @UpdateTime : 2025/8/18 09:04
# -------------------------------
# cron "30 5 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('IKuuu机场签到帐号版')

import os
import re
import random
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def extract_and_select_url():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://ikuuu.club")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    text_content = soup.get_text()
    urls = re.findall(r'ikuuu\.[a-zA-Z0-9]+\b', text_content)

    if urls:
        unique_urls = list(set(urls))
        selected_url = random.choice(unique_urls)
        return selected_url
    else:
        return "未找到网址"


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

DOMAIN= extract_and_select_url()

# 更新 URLs
LOGIN_URL = f"https://{DOMAIN}/auth/login"
CHECKIN_URL = f"https://{DOMAIN}/user/checkin"

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

    print(f"正在处理账号: {account['email']}，使用域名: {DOMAIN}")
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
