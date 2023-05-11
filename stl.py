#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('STLXZ签到')

import requests, json,os

# https://www.stlxz.com/登录后cookie
stl_cookie = os.getenv("stl_cookie")

url = 'https://www.stlxz.com/wp-admin/admin-ajax.php?action=checkin_details_modal'
headers = {
    'cookie': f'{stl_cookie}',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'origin': 'https://www.stlxz.com',
    'referer': 'https://www.stlxz.com/wl/wzzjc/12021.html'
}
data = {
    'action': 'user_checkin'
}
html = requests.post(url=url, headers=headers,data=data)
result = json.loads(html.text)['msg']
print(result)
