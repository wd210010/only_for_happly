#!/usr/bin/python3
# -- coding: utf-8 --
# @Time : 2024/5/7 10:23
# -------------------------------
# cron "30 5 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('宽仔签到');

import requests,json,os

###变量kztk 多账号用&隔开 抓取宽哥之家小程序 点任务抓包 请求头的token
kztk=os.getenv("kztk").split('&')



for i in range(len(kztk)):
    print(f'开始第{i+1}个账号')
    headers = {
        'token': kztk[i],
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x18003030) NetType/WIFI Language/zh_CN miniProgram/wxb6bc0796e0f0db00',
    }
    resp1 = requests.get('https://shop.sctobacco.com/api/mc-server/mcMedia/listForMobile?&offset=0&limit=10&isShow=1',headers=headers)
    result =json.loads(resp1.text)['data']['rows'][0]
    appid = result['appid']
    mediaId = result['mediaId']

    #阅读
    print('开始阅读文章')
    data = {
        'mpMediaId': mediaId,
        'mediaId': mediaId,
        'appid': appid
    }
    resp2 = requests.post('https://shop.sctobacco.com/api/mc-server/mcMedia/clickMedia',headers=headers, data=data)
    result2 =json.loads(resp2.text)
    if result2['code'] ==1:
        print(result2['message'])

    #签到
    print('开始签到')
    resp3= requests.get('https://shop.sctobacco.com/api/ac-server/manage/acSignMemberLog/SignSubmit',headers=headers)
    result3 =json.loads(resp3.text)
    if result3['code']==1:
        print(result3['message'])
    else:
        print(result3['data'])
