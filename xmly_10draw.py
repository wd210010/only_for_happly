#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "6 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('喜马拉雅转盘抽奖')

import requests, json, time ,os

# 写的是喜马拉雅每日十连抽 十连抽一次抓包https://m.ximalaya.com/x-web-activity/draw/activity/drawTenAction这个域名的cookie
# 青龙变量 xmly_cookie
xmly_cookie = os.getenv("xmly_cookie").split('#')

for i in range(3):
    url = 'https://m.ximalaya.com/x-web-activity/draw/activity/drawTenAction'
    headers = {
        'Cookie': f'{xmly_cookie}',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 iting/9.1.3 kdtunion_iting/1.0 iting(main)/9.1.3/ios_1 ;xmly(main)/9.1.3/iOS_1',
    }
    data = {
        'activityId': '2'
    }
    html = requests.post(url=url, headers=headers, data=data)
    if str(json.loads(html.text)['data']['success']) == 'true':
        awardslist = []
        for j in range(len(json.loads(html.text)['data']['awards'])):
            awards = son.loads(html.text)['data']['awards'][j]['description']
            awardslist.append(awards)
        print(
            '抽奖成功! 获得奖品:' + '\n' + str(awardslist).replace('[', '').replace(']', '').replace(',', '\n').replace(
                ' ', '').replace('\'', ''))
    else:
        print(str(json.loads(html.text)['data']['errorMsg']))
    time.sleep(5)
    
    url2 = 'https://m.ximalaya.com/x-web-activity/draw/activity/receivingPercentAward'
    html2 = requests.post(url=url2, headers=headers, data=data)
    if str(json.loads(html2.text)['data']['success']) == 'true':
        print('抽奖成功! ' + '获得奖品' + str(json.loads(html.text)['data']['awards']))
    else:
        print(str(json.loads(html2.text)['data']['errorMsg']))
    time.sleep(5)

