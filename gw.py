#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 6 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('GW树洞机场签到领流量')

import requests
import os
import notify

'''
export gw='邮箱&密码' 多账号#号割开   机场注册地址https://balala.io/auth/register?code=dnL6
'''
def main():
    r = 1
    oy = ql_env()
    print("共找到" + str(len(oy)) + "个账号")
    for i in oy:
        print("------------正在执行第" + str(r) + "个账号----------------")
        email = i.split('&')[0]
        passwd = i.split('&')[1]
        sign_in(email, passwd)
        r += 1
def sign_in(email, passwd):
    try:
        body = {"email" : email,"passwd" : passwd,}
        headers = {'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        resp = requests.session()
        resp.post(f'https://balala.io/auth/login', headers=headers, data=body)
        ss = resp.post(f'https://balala.io/user/checkin').json()
        if 'msg' in ss:
            print(ss['msg'])
            notify.send("GW树洞机场签到领流量", ss['msg'])
    except:
        print('账号密码错')
        notify.send("GW树洞机场签到领流量", '账号密码错')
def ql_env():
    if "gw" in os.environ:
        token_list = os.environ['gw'].split('#')
        if len(token_list) > 0:
            return token_list
        else:
            print("gw变量未启用")
            sys.exit(1)
    else:
        print("未添加gw变量")
        sys.exit(0)

if __name__ == '__main__':
    main()
