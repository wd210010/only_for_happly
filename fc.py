#!/usr/bin/python3
# -- coding: utf-8 --
# @Time : 2024/8/10 9:23
# -------------------------------
# cron "30 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('福彩活动');
#活动地址:https://rf24-h1.cwlo.com.cn/?inviterId=15287&from=qr或者https://rf24-h1.cwlo.com.cn/?inviterId=24889&from=qr
#变量名fcau  抓取https://rf24-serv.cwlo.com.cn这个域名下的Authorization 如果填配置文件就用&隔开 或者一个个的加入环境变量
import requests,json,os

aulist=os.getenv("fcau").split('&')

print(f'获取到{len(aulist)}个账号'+'\n'+'*'*20)
for au in range(len(aulist)):
    print(f'开始执行账号{au+1}')
    try:
        headers = {
            "Authorization": aulist[au],
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.47(0x18002f2c) NetType/WIFI Language/zh_CN",
        }
        #获取阳光列表
        print('开始获取阳光列表>>')
        resp1 = requests.post('https://rf24-serv.cwlo.com.cn/api/user/sun/list', headers=headers,data='last_id=')
        sunlist = json.loads(resp1.text)['data']['list']
        for i in sunlist:
            sunid = i['id']
            print(sunid)
            #收获阳光
            print('开始获取阳光>>')
            data = {'id':sunid}
            resp_getsun=requests.post('https://rf24-serv.cwlo.com.cn/api/user/sun/status', headers=headers,data=data)
            print(resp_getsun.text)
        #获取花朵数
        print('开始获取花朵数>>')
        resp2 = requests.post('https://rf24-serv.cwlo.com.cn/api/user/info', headers=headers)
        flower = json.loads(resp2.text)['data']['user']['flower']
        print(f'当前剩余花朵{flower}')
        # 赠花
        if flower ==0:
            print('不执行赠花')
        else:
            for a in range(flower):
                print('开始赠送花朵>>')
                response = requests.post('https://rf24-serv.cwlo.com.cn/api/welfare/donation', headers=headers)
                print(response.text)
        #获取抽奖次数
        resp3 = requests.post('https://rf24-serv.cwlo.com.cn/api/lottery/user', headers=headers)
        lottery_count = json.loads(resp3.text)['data']['lottery_count']
        print(f'剩余抽检抽奖次数{lottery_count}')
        #抽奖
        if lottery_count ==0:
            print('不执行抽奖')
        else:
            for b in range(lottery_count):
                resp4 = requests.post('https://rf24-serv.cwlo.com.cn/api/lottery/start', headers=headers)
                print(resp4.text)
    except:
        print('该账号失效')
        continue
