#!/usr/bin/python3
# -- coding: utf-8 --
# @Time : 2023/8/2 10:23
# -------------------------------
# cron "30 0,7 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('抽牛奶');

import requests,json,os


# pushtoken
plustoken=os.getenv("plustoken")

#活力伊利小程序 进入小程序后弹窗 中国健儿大运会夺金牌点进去
#抓包access-token https://msmarket.msx.digitalyili.com/域名下的请求头access-token值
mntoken =os.getenv("mntoken").split('&')


def Push(contents):
    #推送加
        headers = {'Content-Type': 'application/json'}
        json = {"token": plustoken, 'title': '蒙牛抽牛奶', 'content': contents.replace('\n', '<br>'), "template": "json"}
        resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
        print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')


for i in range(len(mntoken)):
    print(f'开始第{i+1}个号抽奖')
    try:
        headers = {
            'access-token': mntoken[i],
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.39(0x18002733) NetType/4G Language/zh_CN',
        }
        resp = requests.get('https://msmarket.msx.digitalyili.com/gateway/api/upgrade/lottery/luckDraw?activityId=1684040612280127489',headers=headers)
        result =json.loads(resp.text)['data']['name']
        print('抽奖结果:' + result)
        if '奶' in result:
            Push(contents=result)
    except:
        resp1 = requests.get('https://msmarket.msx.digitalyili.com/gateway/api/upgrade/lottery/luckDraw?activityId=1684040612280127489',headers=headers)
        result1 =json.loads(resp.text)['error']['msg']
        print('抽奖结果:'+result1)
