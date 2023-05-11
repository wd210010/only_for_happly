#!/usr/bin/python3
# -- coding: utf-8 --
# @Time : 2023/4/26 14:22
# -------------------------------
# cron "30 5,7 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('丽宝乐园小程序签到');

import requests, json
import os

# 青龙变量 export blh_hd= ''    抓包https://m.mallcoo.cn/api/user/User/GetRewardList 的请求体
# 变量类似 {"MallID":11192,"Header":{"Token":"*******,16214","systemInfo":{"model":"iPhone13<iPhone14,5>","SDKVersion":"2.30.4","system":"iOS15.6","version":"8.0.34","miniVersion":"2.5.59.1"}}}
blh_hd = os.getenv("blh_hd").split('&')


headers = {
    'content-type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.34(0x1800222f) NetType/4G Language/zh_CN',
}
for i in range(len(blh_hd)):
    resp = requests.post(url='https://m.mallcoo.cn/api/user/User/CheckinV2', headers=headers, data=blh_hd[i])
    result = json.loads(resp.text)['d']['NickName'] + '\n' + json.loads(resp.text)['d']['Msg']
    print(result)
