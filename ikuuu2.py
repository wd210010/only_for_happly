#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/3/27 13:23
# -------------------------------
# cron "30 5 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('IKuuu机场签到帐号版')

import requests,re


import requests
import os
import notify

# export ikuuu='邮箱&密码'      多号#号隔开

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
        res = requests.get('https://ikuuu.me/', headers=headers)
        url = re.findall('target="_blank">(.*?)</a>', res.text, re.S)
        for i in range(len(url)):
            resp = requests.session()
            resp.post(f'{url[i]}auth/login', headers=headers, data=body)
            ss = resp.post(f'{url[i]}user/checkin').json()
    #         print(ss)
            if 'msg' in ss:
                print(ss['msg'])
                notify.send("IKuuu机场签到", ss['msg'])
                break
    except:
        print('请检查帐号配置是否错误')
        notify.send("IKuuu机场签到", '请检查帐号配置是否错误')
def ql_env():
    if "ikuuu" in os.environ:
        token_list = os.environ['ikuuu'].split('#')
        if len(token_list) > 0:
            return token_list
        else:
            print("ikuuu变量未启用")
            sys.exit(1)
    else:
        print("未添加ikuuu变量")
        sys.exit(0)

if __name__ == '__main__':
    main()
