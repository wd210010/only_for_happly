#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('什么值得买签到')

import requests, json,time,hashlib,os

# 青龙变量 zdm_cookie
zdm_cookie = os.getenv("zdm_cookie").split('&')

for i in range(len(zdm_cookie)):
    print(f'开始第{i + 1}个帐号签到')
    ts =int(round(time.time() * 1000))
    url = 'https://user-api.smzdm.com/robot/token'
    headers = {
        'Host': 'user-api.smzdm.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': f'{zdm_cookie[i]}',
        'User-Agent': 'smzdm_android_V10.4.1 rv:841 (22021211RC;Android12;zh)smzdmapp',
    }
    data={
        "f":"android",
        "v":"10.4.1",
        "weixin":1,
        "time":ts,
        "sign":hashlib.md5(bytes(f'f=android&time={ts}&v=10.4.1&weixin=1&key=apr1$AwP!wRRT$gJ/q.X24poeBInlUJC',encoding='utf-8')).hexdigest().upper()
    }
    html = requests.post(url=url, headers=headers, data=data)
    result = html.json()
    token= result['data']['token']

    Timestamp =int(round(time.time() * 1000))
    data={
        "f":"android",
        "v":"10.4.1",
        "sk":"ierkM0OZZbsuBKLoAgQ6OJneLMXBQXmzX+LXkNTuKch8Ui2jGlahuFyWIzBiDq/L",
        "weixin":1,
        "time":Timestamp,
        "token":token,
        "sign":hashlib.md5(bytes(f'f=android&sk=ierkM0OZZbsuBKLoAgQ6OJneLMXBQXmzX+LXkNTuKch8Ui2jGlahuFyWIzBiDq/L&time={Timestamp}&token={token}&v=10.4.1&weixin=1&key=apr1$AwP!wRRT$gJ/q.X24poeBInlUJC',encoding='utf-8')).hexdigest().upper()
    }
    url = 'https://user-api.smzdm.com/checkin'
    url2 = 'https://user-api.smzdm.com/checkin/all_reward'
    headers = {
        'Host': 'user-api.smzdm.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': f'{zdm_cookie[i]}',
        'User-Agent': 'smzdm_android_V10.4.1 rv:841 (22021211RC;Android12;zh)smzdmapp',
    }
    html = requests.post(url=url, headers=headers, data=data)
    html2 = requests.post(url=url2, headers=headers, data=data)
    result = json.loads(html.text)['error_msg']
    result2 = json.loads(html2.text)
    print(result)
    print(result2)
