#!/usr/bin/python3
# -- coding: utf-8 -- 
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2024/5/4 16:23
# -------------------------------
# cron "0 0 2 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('夸克签到')
#搬运至https://github.com/BNDou/Auto_Check_In
#抓包浏览器访问-https://pan.quark.cn/ 并登录 抓取cookie全部 填入青龙变量 环境变量名为 COOKIE_QUARK，多账户用 回车 或 && 分开 

import os
import re
import sys
import requests



#推送函数
# 推送加
plustoken = os.getenv("plustoken")
def Push(contents):
    # 推送加
    headers = {'Content-Type': 'application/json'}
    json = {"token": plustoken, 'title': '夸克签到', 'content': contents.replace('\n', '<br>'), "template": "json"}
    resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
    print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')

# 获取环境变量
def get_env():
    # 判断 COOKIE_QUARK是否存在于环境变量
    if "COOKIE_QUARK" in os.environ:
        # 读取系统变量以 \n 或 && 分割变量
        cookie_list = re.split('\n|&&',os.environ.get('COOKIE_QUARK') ) #os.environ.get('COOKIE_QUARK')
    else:
        # 标准日志输出
        print('❌未添加COOKIE_QUARK变量')
        # send('夸克自动签到', '❌未添加COOKIE_QUARK变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


class Quark:
    def __init__(self, cookie):
        self.cookie = cookie

    def get_growth_info(self):
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info"
        querystring = {"pr": "ucpro", "fr": "pc", "uc_param_str": ""}
        headers = {
            "content-type": "application/json",
            "cookie": self.cookie
        }
        response = requests.get(url=url, headers=headers, params=querystring).json()
        if response.get("data"):
            return response["data"]
        else:
            return False

    def get_growth_sign(self):
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign"
        querystring = {"pr": "ucpro", "fr": "pc", "uc_param_str": ""}
        payload = {"sign_cyclic": True}
        headers = {
            "content-type": "application/json",
            "cookie": self.cookie
        }
        response = requests.post(url=url, json=payload, headers=headers, params=querystring).json()
        if response.get("data"):
            return True, response["data"]["sign_daily_reward"]
        else:
            return False, response["message"]

    def get_account_info(self):
        url = "https://pan.quark.cn/account/info"
        querystring = {"fr": "pc", "platform": "pc"}
        headers = {
            "content-type": "application/json",
            "cookie": self.cookie
        }
        response = requests.get(url=url, headers=headers, params=querystring).json()
        if response.get("data"):
            return response["data"]
        else:
            return False

    def do_sign(self):
        msg = ""
        # 验证账号
        account_info = self.get_account_info()
        if not account_info:
            msg = f"\n❌该账号登录失败，cookie无效"
        else:
            log = f" 昵称: {account_info['nickname']}"
            msg += log + "\n"
            # 每日领空间
            growth_info = self.get_growth_info()
            if growth_info:
                if growth_info["cap_sign"]["sign_daily"]:
                    log = f"✅ 执行签到: 今日已签到+{int(growth_info['cap_sign']['sign_daily_reward'] / 1024 / 1024)}MB，连签进度({growth_info['cap_sign']['sign_progress']}/{growth_info['cap_sign']['sign_target']})"
                    msg += log + "\n"
                    Push(contents=msg)
                else:
                    sign, sign_return = self.get_growth_sign()
                    if sign:
                        log = f"✅ 执行签到: 今日签到+{int(sign_return / 1024 / 1024)}MB，连签进度({growth_info['cap_sign']['sign_progress'] + 1}/{growth_info['cap_sign']['sign_target']})"
                        msg += log + "\n"
                        Push(contents=msg)
                    else:
                        msg += f"✅ 执行签到: {sign_return}\n"

        return msg


def main():
    msg = ""
    global cookie_quark
    
    cookie_quark = get_env()

    print("✅检测到共", len(cookie_quark), "个夸克账号\n")

    i = 0
    while i < len(cookie_quark):
        # 开始任务
        log = f"🙍🏻‍♂️ 第{i + 1}个账号"
        msg += log
        # 登录
        log = Quark(cookie_quark[i]).do_sign()
        msg += log + "\n"

        i += 1

    print(msg)

    return msg[:-1]


if __name__ == "__main__":
    print("----------夸克网盘开始尝试签到----------")
    main()
    print("----------夸克网盘签到执行完毕----------")
