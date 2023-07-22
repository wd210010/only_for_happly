#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2023/7/22 13:23
# -------------------------------
# cron "5 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('茄皇互助');


import requests, json, time, hashlib,os


qhbody = os.getenv("tyqhAccount").split('@')
print(f'共找到{len(qhbody)}个账号,前{round(len(qhbody)/3)}个账号可以吃到助力!!!')

needhelplist=[]
for item in range(round(len(qhbody)/3)):
    Timestamp = int(round(time.time() * 1000))
    signature = hashlib.md5(bytes(
        'clientKey=IfWu0xwXlWgqkIC7DWn20qpo6a30hXX6&clientSecret=A4rHhUJfMjw2I5CODh5g40Ja1d3Yk1CH&nonce=v4sVzP4OhquCSoCh&timestamp=' + f'{Timestamp}',
        encoding='utf-8')).hexdigest().upper()
    # print(signature)
    sign_url = f'https://qiehuang-apig.xiaoyisz.com/qiehuangsecond/ga/public/api/login?signature={signature}&timestamp={Timestamp}&nonce=v4sVzP4OhquCSoCh'
    sign_headers = {
        'Host': 'qiehuang-apig.xiaoyisz.com',
        'Content-Type': 'application/json',
        'Origin': 'https://thekingoftomato.ioutu.cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.29(0x18001d2f) NetType/4G Language/zh_CN miniProgram/wx532ecb3bdaaf92f9',
        'Referer': 'https://thekingoftomato.ioutu.cn/',
        'Content-Length': '134',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    }
    sign_data = f'{qhbody[item]}'

    re = requests.post(url=sign_url, headers=sign_headers, data=sign_data)
    Authorization = json.loads(re.text)['data']['token']
    # print(Authorization)

    headers = {
        'Host': 'qiehuang-apig.xiaoyisz.com',
        'Content-Type': 'application/json',
        'Origin': 'https://thekingoftomato.ioutu.cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.29(0x18001d2f) NetType/4G Language/zh_CN miniProgram/wx532ecb3bdaaf92f9',
        'Authorization': f'{Authorization}',
        'Referer': 'https://thekingoftomato.ioutu.cn/',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    }
    #获取id
    resp = requests.get('https://qiehuang-apig.xiaoyisz.com/qiehuangsecond/ga/user-land/get',headers=headers)
    id = json.loads(resp.text)['data']['gaUserLandList'][0]['userId']
    needhelplist.append(id)
print(needhelplist)
for i in range(len(needhelplist)):
    print(f'开始助力第{i+1}个账号')
    p = qhbody[i*3+1:i*3+4]
    for item in range(len(p)):
        Timestamp = int(round(time.time() * 1000))
        signature = hashlib.md5(bytes(
            'clientKey=IfWu0xwXlWgqkIC7DWn20qpo6a30hXX6&clientSecret=A4rHhUJfMjw2I5CODh5g40Ja1d3Yk1CH&nonce=v4sVzP4OhquCSoCh&timestamp=' + f'{Timestamp}',
            encoding='utf-8')).hexdigest().upper()
        # print(signature)
        sign_url = f'https://qiehuang-apig.xiaoyisz.com/qiehuangsecond/ga/public/api/login?signature={signature}&timestamp={Timestamp}&nonce=v4sVzP4OhquCSoCh'
        sign_headers = {
            'Host': 'qiehuang-apig.xiaoyisz.com',
            'Content-Type': 'application/json',
            'Origin': 'https://thekingoftomato.ioutu.cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.29(0x18001d2f) NetType/4G Language/zh_CN miniProgram/wx532ecb3bdaaf92f9',
            'Referer': 'https://thekingoftomato.ioutu.cn/',
            'Content-Length': '134',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        }
        sign_data = f'{p[item]}'

        re = requests.post(url=sign_url, headers=sign_headers, data=sign_data)
        Authorization = json.loads(re.text)['data']['token']
        # print(Authorization)

        headers = {
            'Host': 'qiehuang-apig.xiaoyisz.com',
            'Content-Type': 'application/json',
            'Origin': 'https://thekingoftomato.ioutu.cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.29(0x18001d2f) NetType/4G Language/zh_CN miniProgram/wx532ecb3bdaaf92f9',
            'Authorization': f'{Authorization}',
            'Referer': 'https://thekingoftomato.ioutu.cn/',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        }
        try:
            resp_zl = requests.get(f'https://qiehuang-apig.xiaoyisz.com/qiehuangsecond/ga/friend-help/help?userId={needhelplist[i]}&type=0',headers=headers)
            result_zl = json.loads(resp_zl.text)
            print(result_zl['message'].replace('\n\n\n',' '))
        except:
            print('助力失败！检查助力账号格式是否正确！')
           
