#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 6 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('IKuuu机场签到领流量')

import requests, json,re,os

#https://ikuuu.dev/user登录后cookie
#IKuuu机场签到领流量
ikuuu_cookie = os.getenv("ikuuu_cookie")

url_info = 'https://ikuuu.art/user/profile'
url = 'https://ikuuu.art/user/checkin'
headers = {
    'cookie': f'{ikuuu_cookie}',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
}
html_info = requests.get(url=url_info, headers=headers).text
html = requests.post(url=url, headers=headers)
result = json.loads(html.text)['msg']
info = "".join(re.findall('<div class="d-sm-none d-lg-inline-block">(.*?)</div>', html_info, re.S))
print(info+'\n'+result)

