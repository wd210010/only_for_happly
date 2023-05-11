#!/usr/bin/python3
# -- coding: utf-8 --
# @Time : 2023/05/08 10:23
# -------------------------------
# cron "0 0 17 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('500w');

import requests
import random
import os
import json

# 推送加
plustoken = os.getenv("plustoken")

#推送函数
def Push(contents):
    # 推送加
    headers = {'Content-Type': 'application/json'}
    json = {"token": plustoken, 'title': '双色球2注', 'content': contents.replace('\n', '<br>'), "template": "json"}
    resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
    print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')

headers ={
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
}
data ={
    "limit":200,
    "page":1,
    "params":{}
}
resp = requests.post('https://ms.zhcw.com/proxy/lottery-chart-center/history/SSQ',headers=headers,data=json.dumps(data))
data = json.loads(resp.text)['datas']
# print(data)

redbulllist =[]
bruebulllist =[]
for i in range(len(data)):
    issue = data[i]['issue']
    redbull = data[i]['winningFrontNum'].split(' ')
    bruebull = data[i]['winningBackNum']
    bruebulllist.append(bruebull)
    redbulllist.append(redbull)

#定位函数
def find_all_index(lst, target):
    indices = []
    for i, value in enumerate(lst):
        if value == target:
            indices.append(i)
    return indices
print('为你生成2注双色球号码如下')
msg = []
for qul in range(2):

    # 统计每红球号码的出现次数
    count_red = [0] * 33
    for bull in redbulllist:
        for num in bull:
            count_red[int(num)-1] += 1
    #去出现次数最少的几个
    min_ten = sorted(count_red)[:10]
    # print(min_ten)
    #定位所在位置数字
    allred =[]
    for a in range(10):
        red = find_all_index(count_red,min_ten[a])
        for b in range(len(red)):
            allred.append(red[b]+1)
    finallist = sorted(list(set(allred)))
    # print(finallist)


    # 统计每篮球号码的出现次数
    count_brue = [0] * 16
    for bull in bruebulllist:
        count_brue[int(bull)-1] += 1
    # print(count_brue)
    min_3 = sorted(count_brue)[:5]
    # print(min_3)
    #定位所在位置数字
    allbrue =[]
    for a in range(5):
        brue = find_all_index(count_brue,min_3[a])
        for b in range(len(brue)):
            allbrue.append(brue[b]+1)
    finallist2 = sorted(list(set(allbrue)))
    # print(finallist2)
    msg.append(str(sorted(random.sample(finallist,6)))+ ' - '+str(sorted(random.sample(finallist2,1))))
massage = str(msg).replace('\', \'','\n').replace('[','').replace(']','').replace('\'','')
print(massage)
Push(contents=massage)
