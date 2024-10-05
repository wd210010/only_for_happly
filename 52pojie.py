#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
青龙脚本
吾爱破解论坛自动签到
变量：PJ52_COOKIE
变量值只需要这二个：htVC_2132_auth和htVC_2132_saltkey
示列：htVC_2132_saltkey=xxxxxx;htVC_2132_auth=xxxxxxx;
在Cookie中查找
定时替则: 30 7 * * *
new Env('吾爱破解签到');
"""
import json
import os
import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup

# pushplus推送函数
def pushplus_notify(title, content):
    PUSH_PLUS_TOKEN = os.getenv("PUSH_PLUS_TOKEN")
    PUSH_PLUS_USER = os.getenv("PUSH_PLUS_USER")

    data = {
        "token": PUSH_PLUS_TOKEN,
        "user": PUSH_PLUS_USER,
        "title": title,
        "content": content
    }
    url = 'http://www.pushplus.plus/send'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url=url, data=json.dumps(data), headers=headers)
    return response.text
    
# 多cookie使用&分割
cookies = ""
if cookies == "":
    if os.environ.get("PJ52_COOKIE"):
        cookies = os.environ.get("PJ52_COOKIE")
    else:
        print("请在环境变量填写PJ52_COOKIE的值")
        sys.exit()
n = 1
for cookie in cookies.split("&"):
    url1 = "https://www.52pojie.cn/CSPDREL2hvbWUucGhwP21vZD10YXNrJmRvPWRyYXcmaWQ9Mg==?wzwscspd=MC4wLjAuMA=="
    url2 = 'https://www.52pojie.cn/home.php?mod=task&do=apply&id=2&referer=%2F'
    url3 = 'https://www.52pojie.cn/home.php?mod=task&do=draw&id=2'
    cookie = urllib.parse.unquote(cookie)
    cookie_list = cookie.split(";")
    cookie = ''
    for i in cookie_list:
        key = i.split("=")[0]
        if "htVC_2132_saltkey" in key:
            cookie += "htVC_2132_saltkey=" + urllib.parse.quote(i.split("=")[1]) + "; "
        if "htVC_2132_auth" in key:
            cookie += "htVC_2132_auth=" + urllib.parse.quote(i.split("=")[1]) + ";"
    if not ('htVC_2132_saltkey' in cookie or 'htVC_2132_auth' in cookie):
        print("第{n}cookie中未包含htVC_2132_saltkey或htVC_2132_auth字段，请检查cookie")
        sys.exit()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/109.0.0.0 Safari/537.36",
    }
    r = requests.get(url1, headers=headers, allow_redirects=False)
    s_cookie = r.headers['Set-Cookie']
    cookie = cookie + s_cookie
    headers['Cookie'] = cookie
    r = requests.get(url2, headers=headers, allow_redirects=False)
    s_cookie = r.headers['Set-Cookie']
    cookie = cookie + s_cookie
    headers['Cookie'] = cookie
    r = requests.get(url3, headers=headers)
    r_data = BeautifulSoup(r.text, "html.parser")
    jx_data = r_data.find("div", id="messagetext").find("p").text
    if "您需要先登录才能继续本操作" in jx_data:
        print(f"第{n}个账号Cookie 失效")
        message = f"第{n}个账号Cookie 失效"
    elif "恭喜" in jx_data:
        print(f"第{n}个账号签到成功")
        message = f"第{n}个账号签到成功"
    elif "不是进行中的任务" in jx_data:
        print(f"第{n}个账号今日已签到")
        message = f"第{n}个账号今日已签到"
    else:
        print(f"第{n}个账号签到失败")
        message = f"第{n}个账号签到失败"
    n += 1
    pushplus_notify("吾爱签到", message)
