#!/usr/bin/python3
# -- coding: utf-8 --
# @Time : 2023/4/8 10:23
# -------------------------------
# cron "30 5 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('阿里云盘签到');

import json
import  requests
import  os

##变量export ali_refresh_token=''
ali_refresh_token=os.getenv("ali_refresh_token").split('&')
#refresh_token是一成不变的呢，我们使用它来更新签到需要的access_token
#refresh_token获取教程：https://github.com/bighammer-link/Common-scripts/wiki/%E9%98%BF%E9%87%8C%E4%BA%91%E7%9B%98refresh_token%E8%8E%B7%E5%8F%96%E6%96%B9%E6%B3%95
# ali_refresh_token = os.getenv("ali_refresh_token")
# 推送加
plustoken = os.getenv("plustoken")


#推送函数
def Push(contents):
    # 推送加
    headers = {'Content-Type': 'application/json'}
    json = {"token": plustoken, 'title': 'aliyun签到', 'content': contents.replace('\n', '<br>'), "template": "json"}
    resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
    print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')

#签到函数
for i in range(len(ali_refresh_token)):
    print(f'开始帐号{i+1}签到')
    def daily_check(access_token):
        url = 'https://member.aliyundrive.com/v1/activity/sign_in_list'
        headers = {
            'Authorization': access_token
        }
        response = requests.post(url=url, headers=headers, json={}).text
        result = json.loads(response)
        if 'success' in result:
            print('签到成功')
            for i, j in enumerate(result['result']['signInLogs']):
                if j['status'] == 'miss':
                    day_json = result['result']['signInLogs'][i-1]
                    # print(day_json)
                    if not day_json['isReward']:
                        contents = '签到成功，今日未获得奖励'
                    else:
                        contents = '本月累计签到{}天,今日签到获得{}{}'.format(result['result']['signInCount'],
                                                                         day_json['reward']['name'],
                                                                         day_json['reward']['description'])
                    print(contents)

                    return contents


    # 使用refresh_token更新access_token
    def update_token(refresh_token):
        url = 'https://auth.aliyundrive.com/v2/account/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': ali_refresh_token[i]
        }
        response = requests.post(url=url, json=data).json()
        access_token = response['access_token']
#         print('获取的access_token为{}'.format(access_token))
        return access_token


    def mian():
#         print('更新access_token')
        access_token = update_token(ali_refresh_token)
#         print('更新成功，开始进行签到')
        content = daily_check(access_token)
        if plustoken != '':
            Push(content)

    if __name__ == '__main__':
        mian()
