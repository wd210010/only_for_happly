# #达美乐,开一把游戏抓取openid的值
# 变量名dmlck
import os
import time
import requests
import json
import notify

message = ''
from dotenv import load_dotenv
load_dotenv()
accounts = os.getenv('dmlck')
#推送加 token
plustoken = os.getenv("plustoken")

def Push(contents):
  # plustoken推送
    headers = {'Content-Type': 'application/json'}
    json = {"token": plustoken, 'title': '达美乐披萨中奖推送', 'content': contents.replace('\n', '<br>'), "template": "json"}
    resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
    print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')

if accounts is None:
    print('叼毛CK都没跑个毛啊？')
else:
    accounts_list = os.environ.get('dmlck').split('&')

    num_of_accounts = len(accounts_list)

    print(f"获取到 {num_of_accounts} 个账号")

    for i ,account in enumerate(accounts_list, start=1):

        values = account.split(',')

        Cookie = values[0]

        print(f"\n=======达美乐开始执行账号{i}=======")

        url = "https://game.dominos.com.cn/bulgogi/game/gameDone"

        payload = f"openid={Cookie}&score=d8XtWSEx0zRy%2BxdeJriXZeoTek6ZVZdadlxdTFiN9yrxt%2BSIax0%2BRccbkObBZsisYFTquPg%2FG2cnGPBlGV2f32C6D5q3FFhgvcfJP9cKg%2BXs6l7J%2BEcahicPml%2BZWp3P4o1pOQvNdDUTQgtO6NGY0iijZ%2FLAmITy5EJU8dAc1EnbvhOYG36Qg1Ji4GDRoxAfRgmELvpLM6JSFlCEKG2C2s%2BJCevOJo7kwsLJCvwbVgeewhKSAyCZYnJQ4anmPgvrv6iUIiFQP%2Bj6%2B5p1VETe5xfawQ4FQ4w0mttXP0%2BhX39n1dzDrfcSkYkUaWPkIFlHAX7QPT3IgG6MhIKCvB%2BUcw%3D%3D&tempId=16408240716151126162"

        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 12; M2012K11AC Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/122.0.6261.120 Mobile Safari/537.36 XWEB/1220133 MMWEBSDK/20240404 MMWEBID/8518 MicroMessenger/8.0.49.2600(0x2800313D) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
            'Accept-Encoding': "gzip,compress,br,deflate",
            'Content-Type': "application/x-www-form-urlencoded",
            'charset': "utf-8",
            'Referer': "https://servicewechat.com/wx887bf6ad752ca2f3/63/page-frame.html"
        }

        while True:
            shrurl = "https://game.dominos.com.cn/bulgogi/game/sharingDone"
            payload2 = f"openid={Cookie}&from=1&target=0"
            res = requests.post(shrurl, data=payload2, headers=headers).json()
            if res['errorMessage'] == "今日分享已用完，请明日再来":
                print(f'账号{i}分享已达上限，明天再来吧')
                break
        for a in range(3):
            response = requests.post(url, data=payload, headers=headers)
            response = response.json()
            if response["statusCode"] == 0:
                prize = response['content']['name']
                print(f"\n账号{i}\n{prize}")
                message += f"\n{prize}"
                if '一等奖' in prize:
                    Push(contents="账号{i}\n{prize}")
            if response["statusCode"] != 0:
                print(response)
                err = response['errorMessage']
                message += f'\n账号{i}\n {err}'
                break
try:
    notify.send('达美乐',message)
except Exception as e:
    print(e)
    print('推送失败')
