
#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 1 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('逑美在线')

import requests, json,time,re,os

# 逑美在线app 可以完成签到和抽卡人任务
# qmzxbody取app登录(使用帐号密码登录)界面登录后的https://api.qiumeiapp.com/qm/10001/qmLogin URL的请求body全部 放到单引号里面 多账号支持
# 示例'{"deviceNumber":"*****","anonymousId":"*****","appVersion":"7.2.1","appMarket":"appstore","password":"*****","deviceModel":"iPhone14,5","sign":"******","deviceToken":"*****==","phoneNumber":"*****"}',

# 青龙变量 qmzxbody
qmzxbody = os.getenv("qmzxbody").split('&')


#推送加 token
plustoken = os.getenv("plustoken")

def Push(contents):
  # plustoken推送
    headers = {'Content-Type': 'application/json'}
    json = {"token": plustoken, 'title': '逑美抽卡', 'content': contents.replace('\n', '<br>'), "template": "json"}
    resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
    print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')


# 获取token
for i in range(len(qmzxbody)):
    sign = "".join(re.findall('"sign":"(.*?)"', qmzxbody[i], re.S))
    # print(sign)
    url = 'https://api.qiumeiapp.com/qm/10001/qmLogin'
    headers = {
        'Host': 'api.qiumeiapp.com',
        'Content-Type': 'application/json',
        'appVersion': '8.1.1',
        'Content-Length': '425',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'qiu mei zai xian/7.2.0 (iPhone; iOS 15.6; Scale/3.00)',
        'Accept-Language': 'zh-Hans-CN;q=1',
        'Accept-Encoding': 'gzip, deflate, br',
        'appMarket': 'appstore-qmzx'
    }
    data = f"{qmzxbody[i]}"
    html = requests.post(url=url, headers=headers, data=data)
    data_1 = json.loads(html.text)
    print(f"账号{i+1}-"+data_1['data']['phoneNumber'])
    is_true = data_1['msg']
    if is_true == "登录成功!":
        print('登录成功')
    else:
        print('登录失败!')
    # 获取token
    qmUserToken = data_1['data']['qmUserToken']
    url_qd  ='https://api.qiumeiapp.com/qm-activity/qdcj/signin'
    headers = {
        'Host': 'api.qiumeiapp.com',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://h5.qiumeiapp.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Umeng4Aplus/1.0.0',
        'Referer': 'https://h5.qiumeiapp.com/',
        'Content-Length': '52',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    }
    data = f'qmUserToken={qmUserToken}'
    html_qd = requests.post(url=url_qd, headers=headers, data=data)
    data_3 = json.loads(html_qd.text)
    print(data_3['msg'])
    # 抽卡
    url_ck = 'https://api.qiumeiapp.com/qm-activity/qdcj/luckyDraw'
    html_2 = requests.post(url=url_ck, headers=headers, data=data)
    data_2 = json.loads(html_2.text)
    print(data_2['msg'])

    # url_r ='https://api.qiumeiapp.com/qm/10005/qmAchievePointChannel'
    # data_r ={
    #     "channelCode":"READ_CONTENT",
    #     "sign":f"{sign}",
    #     "qmUserToken":f"{qmUserToken}"
    # }
    # html_r =requests.post(url=url_r, headers=headers, data=data_r).text
    # print(html_r)

    url_user ='https://api.qiumeiapp.com/qmxcx/10001/getQmUserPointInfo'
    url_run ='https://api.qiumeiapp.com/qm-activity/qdcj/getUserSigninInfo'
    url_c ='https://api.qiumeiapp.com/qm-activity/hc/getUserMaterialList'
    token = f'appUserToken={qmUserToken}'
    html_user = requests.post(url=url_user, headers=headers, data=token)
    html_run = requests.post(url=url_run, headers=headers, data=data)
    html_c = requests.post(url=url_c, headers=headers, data=data)
    data_4 = json.loads(html_user.text)
    data_5 = json.loads(html_run.text)
    data_6 = json.loads(html_c.text)['data']['materialList']
    print('本月登录天数: ' + str(data_5['data']['runningDays']) +' 豆豆余额: '+str(data_4['data']['totalAmount']))
    for aa in range(len(data_6)) :
        print(str(data_6[aa]['materialName'])+': '+str(data_6[aa]['haveCount'])+'/1')
        if str(data_6[aa]['materialName'])=="紧致卡" and data_6[aa]['haveCount'] ==1:
            massage1 =str(data_1['data']['phoneNumber']) +'可能集齐了去看看！！！'
            Push(contents=massage1)
        elif str(data_6[aa]['materialName'])=="全能卡" and data_6[aa]['haveCount'] ==1:
            massage2 =str(data_1['data']['phoneNumber']) +'可能集齐了去看看！！！'
            Push(contents=massage2)
    print('*****')
