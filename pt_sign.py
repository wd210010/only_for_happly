#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 1 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('pt站签到')

import requests, json, re,os
from bs4 import BeautifulSoup as bs
import numpy as np

# #https://hdatmos.club/attendance.php
# hdatmos_cookie=['']
# #https://kp.m-team.cc/index.php
# kp_m_team_cookie=['']
# #https://pt.btschool.club/index.php
# btschool_cookie=['']
# #https://www.haidan.video/index.php
# haidan_cookie=['']

# 青龙变量 hdatmos_cookie kp_m_team_cookie btschool_cookie haidan_cookie
hdatmos_cookie = os.getenv("hdatmos_cookie").split('&')
kp_m_team_cookie = os.getenv("kp_m_team_cookie").split('&')
btschool_cookie = os.getenv("btschool_cookie").split('&')
haidan_cookie = os.getenv("haidan_cookie").split('&')

#推送加 token
plustoken = os.getenv("plustoken")

def Push(contents):
  # plustoken推送
    headers = {'Content-Type': 'application/json'}
    json = {"token": plustoken, 'title': 'PT签到', 'content': contents.replace('\n', '<br>'), "template": "json"}
    resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
    print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')

#hdatmos签到
print('开始hdatmos签到')
for i in range(len(hdatmos_cookie)):
    hdatmos_url = 'https://hdatmos.club/attendance.php'
    hdatmos_headers = {
        'cookie': f'{hdatmos_cookie[i]}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Referer': 'https://hdatmos.club/attendance.php',
    }
    re_2 = requests.get(url=hdatmos_url, headers=hdatmos_headers).text
    result = "".join(re.findall('<p>(.*?)<span style="float:right">', re_2, re.S)).replace('<b>', '').replace('</b>','')
    if '签到' in result:
        print('签到成功' + '\n'  + result)
    else:
        login_1=f'检查hdatmos的ck{i+1}是否失效！！！'
        print(login_1)
        Push(contents=login_1)

#kp.m-team签到
print('--------')
print('开始kp.m-team签到')
for i in range(len(kp_m_team_cookie)):
    kp_m_team_url = 'https://kp.m-team.cc/index.php'
    kp_m_team_headers = {
        'cookie': f'{kp_m_team_cookie[i]}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Referer': 'https://kp.m-team.cc/index.php',
    }
    re_3 = requests.get(url=kp_m_team_url, headers=kp_m_team_headers).text
    result_2 = "".join(re.findall('<span class="medium">(.*?), <span class="nowrap">', re_3, re.S)).replace('<b>', '').replace('</b>','')
    if result_2 =='歡迎回來':
        print('签到成功' + '\n' + '返回信息:'+result_2)
    else:
        login_2=f'检查kp.m-team的ck{i+1}是否失效！！！'
        print(login_2)
        Push(contents=login_2)

#btschool签到
print('--------')
print('开始btschool签到')
for i in range(len(kp_m_team_cookie)):
    btschool_url = 'https://pt.btschool.club/index.php'
    btschool_headers = {
        'cookie': f'{btschool_cookie[i]}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Referer': 'https://pt.btschool.club/index.php',
    }
    re_4 = requests.get(url=btschool_url, headers=btschool_headers).text
    result_3 = "".join(re.findall('<span class="medium">(.*?), <span class="nowrap">', re_4, re.S))
    if result_3 =='欢迎回来':
        print('签到成功' + '\n' + '返回信息:'+result_3)
    else:
        login_3=f'检查btschool的ck{i+1}是否失效！！！'
        print(login_3)
        Push(contents=login_3)

#haidan签到
print('--------')
print('开始haidan签到')
for i in range(len(haidan_cookie)):
    haidan_url_1 = 'https://www.haidan.video/signin.php'
    haidan_url = 'https://www.haidan.video/index.php'
    haidan_headers = {
        'cookie': f'{haidan_cookie[i]}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    re_5= requests.get(url=haidan_url_1, headers=haidan_headers).text
    re_6 = requests.get(url=haidan_url, headers=haidan_headers).text
    result_4 = "".join(re.findall('class="dt_button" value="(.*?)" />', re_6, re.S))
    if result_4 =='已经打卡':
        print('签到成功' + '\n' + '返回信息:'+result_4)
    else:
        login_4=f'检查haidan的ck{i+1}是否失效！！！'
        print(login_4)
        Push(contents=login_4)

