#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happy
# @Time : 2023/7/20 8:23
# -------------------------------
# cron "30 7 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('联想app签到任务')

import requests,json,os

#任务路径 联想手机app-我的-赚乐豆
#青龙变量 lenovohd 为lenovoId,accessToken,serviceToken,Cookie,SERVICE-AUTHENTICATION拼接(中间用@符号隔开) 多账号设置用&符号把多个拼接后的配置隔开
lenovohd = os.getenv("lenovohd").split('&')

for i in range(len(lenovohd)):
    print(f'***账号{i+1}开始任务***')
    lenovoId = lenovohd[0].split('@')[0]
    headers ={
        'Host':'mmembership.lenovo.com.cn',
        'memberIds':'5',
        'lenovoId':lenovoId ,
        'clientId':'2',
        'accessToken':lenovohd[0].split('@')[1],
        'Accept-Language':'zh-CN,zh-Hans;q=0.9',
        'Accept-Encoding':'gzip, deflate, br',
        'Connection':'keep-alive',
        'Origin':'https://mmembership.lenovo.com.cn',
        'tenantId':'25',
        'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148lenovoofficialapp/newversion/D32F5D30-8A08-4C63-9A92-3E7CE5189075_10121112887/versioncode-1000100/',
        'serviceToken':lenovohd[0].split('@')[2],
        'Content-Length':'0',
        'Cookie':lenovohd[0].split('@')[3],
        'SERVICE-AUTHENTICATION':lenovohd[0].split('@')[4]
    }
    #签到
    respCheckin =requests.post(f'https://mmembership.lenovo.com.cn/member-hp-task-center/v1/task/checkIn?lenovoId={lenovoId}',headers=headers)
    checkinlog = json.loads(respCheckin.text)
    print(checkinlog['msg'])
    #获取任务
    resp = requests.post('https://mmembership.lenovo.com.cn/member-hp-task-center/v1/task/getUserTaskList',headers=headers)
    result = json.loads(resp.text)['data']
    for i in range(len(result)):
        taskId =result[i]['taskId']
        taskName = result[i]['name']
        print(str(taskId)+'----'+taskName)
        #完成任务
        resp2 = requests.post(f'https://mmembership.lenovo.com.cn/member-hp-task-center/v1/checkin/selectTaskPrize?taskId={taskId}&channelId=1',headers=headers)
        resp3 = requests.post(
            f'https://mmembership.lenovo.com.cn/member-hp-task-center/v1/Task/userFinishTask?taskId={taskId}&channelId=1&state=1',
            headers=headers)
        print(json.loads(resp3.text)['msg'])
