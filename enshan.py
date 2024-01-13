#!/usr/bin/python3
# -- coding: utf-8 -- 
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2023/10/4 16:23
# -------------------------------
# cron "0 0 2 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('恩山签到')
import requests,re,os

#配置恩山的cookie 到配置文件config.sh export enshanck='' 需要推送配置推送加token export plustoken=''
enshanck = os.getenv("enshanck")

#推送加 token
plustoken = os.getenv("plustoken")

def Push(contents):
    # 推送加
    headers = {'Content-Type': 'application/json'}
    json = {"token": plustoken, 'title': '恩山签到', 'content': contents.replace('\n', '<br>'), "template": "json"}
    resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
    print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36",
    "Cookie": enshanck,
}
session = requests.session()
response = session.get('https://www.right.com.cn/FORUM/home.php?mod=spacecp&ac=credit&showcredit=1', headers=headers)
try:
    coin = re.findall("恩山币: </em>(.*?)&nbsp;", response.text)[0]
    point = re.findall("<em>积分: </em>(.*?)<span", response.text)[0]
    res = f"恩山币：{coin}\n积分：{point}"
    print(res)
    Push(contents=res)
except Exception as e:
    res = str(e)
