#!/usr/bin/python3 
# -- coding: utf-8 --
# @Time : 2023/6/30 10:23
# -------------------------------
# cron "30 6,8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('雨云签到');

import json,requests,os


##变量雨云账号密码 注册地址https://www.rainyun.com/NTY1NzY=_
yyusername=os.getenv("yyusername")
yypassword=os.getenv("yypassword")


#登录
def login_sign():
    session = requests.session()
    resp1 = session.post('https://api.v2.rainyun.com/user/login',headers={"Content-Type": "application/json"}, data=json.dumps({"field": f"{yyusername}", "password": f"{yypassword}"}))
    if resp1.text.find("200") > -1:
        print("登录成功")
        x_csrf_token = resp1.cookies.get_dict()['X-CSRF-Token']
        # print(x_csrf_token)
    else:
        print(f"登录失败，响应信息：{resp1.text}")



    headers= {
        'x-csrf-token': x_csrf_token,
    }
    resp = session.post('https://api.v2.rainyun.com/user/reward/tasks',headers=headers,data=json.dumps({"task_name": "每日签到","verifyCode": ""}))
    print(json.loads(resp.text)['message'])

if __name__ == '__main__':
    login_sign()

