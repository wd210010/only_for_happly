#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 1 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('千图网签到')

import requests, json ,os
import datetime
import notify

# 青龙变量 qtw_cookie
qtw_cookie = os.getenv("qtw_cookie").split('&')

# gettoken
url1 = 'https://www.58pic.com/index.php?m=ajax&a=getApiToken'
headers1 = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '0',
    'Cookie': f'{qtw_cookie}',
    'Host': 'www.58pic.com',
    'Origin': 'https://www.58pic.com',
    'Referer': 'https://www.58pic.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
html1 = requests.post(url=url1, headers=headers1)
token = json.loads(html1.text)['data']['token']
# print(token)

weekday = datetime.date.today().weekday() + 1
url = 'https://ajax-api.58pic.com/Growing/user-task/index'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}
data = {
    'token': f'{token}'
}
html = requests.post(url=url, headers=headers, data=data)
re = json.loads(html.text)
signDay = re['data']['signDay']
isSign = re['data']['signData'][f'{weekday}']['isSign']
reward = re['data']['signData'][f'{weekday}']['title']
type_1 = re['data']['signData'][f'{weekday}']['type']
if isSign == 1 and type_1 == 1:
    print('今日签到成功！获得VIP：' + reward)
    notify.send("千图网签到", '今日签到成功！获得VIP：' + reward)
elif isSign == 1 and type_1 == 2:
    print('今日签到成功！获得积分：' + reward)
    notify.send("千图网签到", '今日签到成功！获得积分：' + reward)
else:
    print('签到失败！！')
    notify.send("千图网签到", '签到失败！！')
