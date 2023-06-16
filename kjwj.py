#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 7 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('科技玩家签到')

import requests, json, re,os


# 青龙变量 kjwj_username 配置用户名（一般是邮箱）  kjwj_password 配置用户名对应的密码 和上面的username对应上 多账号&隔开
kjwj_username = os.getenv("kjwj_username").split('&')
kjwj_password = os.getenv("kjwj_password").split('&')

for i in range(len(kjwj_username)):
    url = 'https://www.kejiwanjia.com/wp-json/jwt-auth/v1/token'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'origin': 'https://www.kejiwanjia.com',
        'referer': 'https://www.kejiwanjia.com/'
    }
    data = {
        'username': f'{kjwj_username[i]}',
        'password': f'{kjwj_password[i]}'
    }
    html = requests.post(url=url, headers=headers, data=data)
    result = json.loads(html.text)
    name = result['name']
    token = result['token']
    check_url = 'https://www.kejiwanjia.com/wp-json/b2/v1/getUserMission'
    sign_url = 'https://www.kejiwanjia.com/wp-json/b2/v1/userMission'
    sign_headers = {
        'Host': 'www.kejiwanjia.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'authorization': 'Bearer ' + f'{token}',
        'cookie': f'b2_token={token};',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    html_1 = requests.post(url=check_url, headers=sign_headers)
    imfo_1 = json.loads(html_1.text)
    if imfo_1['mission']['credit'] == 0:
        print("开始检查第"+str(i+1)+"个帐号"+ " " +  name +"签到")
        print("还未签到 开始签到")
        html_2 = requests.post(url=sign_url, headers=sign_headers)
        imfo_2 = json.loads(html_2.text)
        print("签到成功 获得" + str(imfo_2)+ "积分")
    else:
        print("帐号" + str(i + 1) + " " + name )
        print("今天已经签到 获得" + str(imfo_1['mission']['credit']) + "积分")
