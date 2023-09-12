#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 9 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('ddnsto七天续费');

import requests, json,uuid,datetime,re,os
from datetime import timedelta

# 配置参数 登录https://www.ddnsto.com/app/#/devices 抓包cookie
ddns_cookie = os.getenv("ddns_cookie")
xcsrftoken=re.findall('csrftoken=(.*?);', ddns_cookie, re.S)[0]
# 先购买一次7天免费套餐 抓包查看https://www.ddnsto.com/api/user/routers/*****/ 这个url里面的*****就是userid
ddns_userid=os.getenv("ddns_userid")

# pushtoken
plustoken=os.getenv("plustoken")


def Push(contents):
    #推送加
        headers = {'Content-Type': 'application/json'}
        json = {"token": plustoken, 'title': 'DDNS', 'content': contents.replace('\n', '<br>'), "template": "json"}
        resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
        print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')
        
# utc-beijing
def UTC2BJS(UTC):
    UTC_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    BJS_format = "%Y-%m-%d %H:%M:%S"
    UTC = datetime.strptime(UTC,UTC_format)
    #格林威治时间+8小时变为北京时间
    BJS = UTC + timedelta(hours=8)
    BJSJ = BJS.strftime(BJS_format)
    return BJSJ


#获取订单号
uu_id = uuid.uuid4()
suu_id = ''.join(str(uu_id).split('-'))
url_2 = 'https://www.ddnsto.com/api/user/product/orders/'
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': f'{ddns_cookie}',
    'referer': 'https://www.ddnsto.com/app/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'x-csrftoken': f'{xcsrftoken}'
}
data_2 = {
    'product_id': '2',
    'uuid_from_client': f'{suu_id}'
}
html_2 = requests.post(url=url_2, headers=headers,data=data_2)
result_2 = json.loads(html_2.text)
if result_2['application-error']=='超出本周免费套餐购买次数':
    print(result_2['application-error'])
    message_3=result_2['application-error']
    Push(contents=message_3)
else:
    id = result_2['id']
    print(id)
    # 提交订单
    url_3 = f'https://www.ddnsto.com/api/user/product/orders/{id}/'
    html_3 = requests.get(url=url_3, headers=headers).text

    #创建
    url_4 =f'https://www.ddnsto.com/api/user/routers/{ddns_userid}/'
    data_4 ={
        "plan_ids_to_add":[f'{id}'],
        "server":3
    }
    html_4 = requests.patch(url=url_4, headers=headers,data =data_4)
    result_4 = json.loads(html_4.text)
    if len(result_4['uid'])>0:
        print('****白嫖成功*****'+'\n'+'到期时间：'+UTC2BJS(result_4['active_plan']["product_expired_at"]))
    else:
        print('没有白嫖到！检查配置看看')
    message_2 = '****白嫖成功*****'+'\n'+'到期时间：'+UTC2BJS(result_4['active_plan']["product_expired_at"])
    Push(contents=message_2)
