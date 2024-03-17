#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "1 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('富贵论坛签到');

import requests, re,time,json,time,os
import notify

# 富贵论坛签到
# export fg_cookies='配置富贵论坛cookie'

fg_cookies = os.getenv("fg_cookies").split('&')


###逐行读取数据
for i in range(len(fg_cookies)):
    cookie = fg_cookies[i]
    url2 = 'https://www.fglt.net/'
    headers2 = {
        'cookie': f'{cookie}',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    re2 = requests.post(url=url2, headers=headers2).text
    formhash = str(re.findall('<input type="hidden" name="formhash" value="(.*?)" />', re2, re.S)).replace('\'', '').replace('[', '').replace(']', '')

    print('获取到formhash:'+ formhash +f'\n***开第{i+1}个账号签到***' )

    #签到
    url4=f'https://www.fglt.net/plugin.php?id=dsu_amupper&ppersubmit=true&formhash={formhash}&infloat=yes&handlekey=dsu_amupper&inajax=1&ajaxtarget=fwin_content_dsu_amupper'
    re4 = requests.post(url=url4, headers=headers2).text
    result =str(re.findall('showDialog\((.*?),', re4, re.S)).replace('\'', '').replace('[', '').replace(']', '').replace('"', '')
    print(result)
    notify.send("富贵论坛签到", result)


