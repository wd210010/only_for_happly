#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "0 7,10 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('浙江福彩抽奖')

#变量export zjfcau='' 多账号&隔开  在关注浙江福彩后-工具栏 服务工具-有奖互动 然后开启抓包 点去抽奖或者我的奖品 抓包gtj-api.shiseidochina.cn域名响应头Authorization 建议设置整点运行
import requests,json,time,os

Authorization=os.getenv("zjfcau").split('&')    

for i in range(10):
    for i in range(len(Authorization)):
        headers ={
            'Authorization':Authorization[i],
            'merchantId':'628',
            'Content-Type':'application/json;charset=utf-8',
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.43(0x18002b29) NetType/WIFI Language/zh_CN',
            'sign':'6d4141c115e28975770a13cf5edf4f72',

        }
        data = '{"actId":698740515,"standardId":33339,"commodityNum":1}'
        resp = requests.post('https://apimeans.luckyop.com/front/api/createOrder/',headers=headers,data=data)
        headers2={
            'Authorization':Authorization[i],
            'merchantId':'628',
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.43(0x18002b29) NetType/WIFI Language/zh_CN',
            'sign':'3e9f34f0f5a6c8462e77a95107132292'

        }
        resp2 =requests.post('https://apimeans.luckyop.com/front/api/get_lottery_info/698740460',headers=headers2)
        headers3={
            'Authorization':Authorization[i],
            'merchantId':'628',
            'Content-Type':'application/json;charset=utf-8',
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.43(0x18002b29) NetType/WIFI Language/zh_CN',
            'sign':'711eecb0d05dcd3c29d2e14cb67c8a8b'
        }
        data3 ='{"actId":698740460}'
        resp3 =requests.post('https://apimeans.luckyop.com/front/api/lottery_draw',headers=headers3,data=data3)
        if json.loads(resp3.text)['status'] ==200:
            print(json.loads(resp3.text)['payload']['prizeName'])
        else:
            print(json.loads(resp3.text)['error'])
        time.sleep(0.5)
