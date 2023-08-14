#!/usr/bin/python3 
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2023/8/14 13:23
# -------------------------------
# cron "30 5,7 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('蜜糖签到')
import requests,json,os

# 蜜糖app签到 购物签到七天返20% 发货目前挺快
# https://channel.mitangwl.cn/h5/spread/index.html?inviteId=198243 点击打开下载app或者小程序下单即可
# 变量为mtau 随便找一个api.mitangwl.cn点进去  请求头里面的Authorization里面的就是 格式如a7f2xxxx-9dxx-46xx-97xx-3e8a7xxxxxxxxx 青龙配置文件config进去设置export mtau=''即可 多账号用&隔开
Authorization =  os.getenv("mtau").split('&')

for i in range(len(Authorization)):
    # 获取列表
    print(f'开始第{i+1}个账号签到！')
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'SeckillShopping/2.5.5 (iPhone; iOS 15.6.1; Scale/3.00)',
        'Authorization': Authorization[i],
        'Accept-Language': 'zh-Hans-CN;q=1',
        'Content-Length': '32'
    }
    data_list = {
        'pageNum': 1,
        'pageSize': 10
    }
    appointmentIdlist =[]
    productNamelist = []
    try:
        resp = requests.post('https://api.mitangwl.cn/app/my/queryMyApprointmentList',headers=headers,data=json.dumps(data_list))
        rt =json.loads(resp.text)['data']['list']
        for j in range(len(rt)):
            appointmentId = rt[j]['appointmentId']
            productName = rt[j]['productName']
            appointmentIdlist.append(appointmentId)
            productNamelist.append(productName)

        for k in range(len(appointmentIdlist)):
            data = {
                'loc':0,
                'appointmentId':appointmentIdlist[k]
            }
            response = requests.post('https://api.mitangwl.cn/app/my/appointmentSign', headers=headers,data=json.dumps(data))
            result = json.loads(response.text)
            print(productNamelist[k]+ ' 签到:'+ result['msg'])
    except:
        print('请检查账号配置是否有误！')
