#!/usr/bin/python3
# -- coding: utf-8 -- 
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2024/1/3 9:23
# -------------------------------
# cron "0 10 2,23 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('农夫山泉抽水')
import requests,json,time,os
from datetime import datetime


#小程序农夫山泉好水旺财龙年吉祥 进去开启抓包点获取次数 然后返回抓包软件 找gateway.jmhd8.com 这个域名下的请求头里面的apitoken
#设置变量为3个 nfsqtoken（为上面获取的apitoken 多号用&分割） nflong nfdim 这两个为抽奖的定位经纬度 拾取经纬度坐标https://api.map.baidu.com/lbsapi/getpoint/index.html?qq-pf-to=pcqq.c2c
#设置了23点以后运行的话会自动抽奖 23点之前默认不抽奖 可以设置23点前运行一次跑任务 23点以后运行一次抽奖
#可以根据哪里有水了 定位到哪里 自行修改经纬度坐标
#配置plustoken可以在抽到龙年水时推送
apitoken = os.getenv("nfsqtoken").split('&')
longitude =  os.getenv("nflong")
dimension =  os.getenv("nfdim")


#推送加 token
plustoken =os.getenv("plustoken")

def Push(contents):
  # plustoken推送
    headers = {'Content-Type': 'application/json'}
    json = {"token": plustoken, 'title': '农夫山泉中奖通知', 'content': contents.replace('\n', '<br>'), "template": "json"}
    resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
    print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')

# 获取当前日期
current_date = datetime.now()
# 将日期格式化为 yyyy-MM-dd 格式
formatted_date = current_date.strftime('%Y-%m-%d')
session =requests.session()
for a in range(len(apitoken)):#
    print(f'开始第{a+1}个账号任务')
    headers ={
        'content-type': 'application/json',
        'apitoken': apitoken[a],
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.45(0x18002d27) NetType/WIFI Language/zh_CN',
    }
    #分享
    print('开始分享任务》》》')
    resp1 =session.get(f'https://gateway.jmhd8.com/geement.marketingplay/api/v1/task/join?action_time={formatted_date}%2007%3A07%3A53&task_id=23122117420818',headers=headers)
    result1 = json.loads(resp1.text)#['success']
    print('结果：'+str(result1['success'])+'---'+result1['msg'])
    time.sleep(2)
    #访问视频号
    print('开始访问视频号任务》》》')
    resp2 =session.get(f'https://gateway.jmhd8.com/geement.marketingplay/api/v1/task/join?action_time={formatted_date}%2021%3A44%3A20&task_id=23122117344230',headers=headers)
    result2 = json.loads(resp2.text)#['success']
    print('结果：'+str(result2['success'])+'---'+result2['msg'])
    time.sleep(2)
    #每日签到
    print('开始每日签到任务》》》')
    resp3 =session.get(f'https://gateway.jmhd8.com/geement.marketingplay/api/v1/task/join?action_time={formatted_date}%2021%3A44%3A15&task_id=23122117321925',headers=headers)
    result3 = json.loads(resp3.text)#['success']
    print('结果：'+str(result3['success'])+'---'+result3['msg'])
    time.sleep(2)

    #获取openid
    resp4 =session.get(f' https://gateway.jmhd8.com/geement.usercenter/api/v1/user/information?levelprocessinfo=false&gpslocationinfo=false&popularizeinfo=false&disablequery_extra_field=true&disablequery_location=true&disablequery_memberinfo=true&disablequery_customfield=true&disablequery_levelinfo=true&disablequery_perfectinfo_status=true&disablequery_extrainformation=true',headers=headers)
    user_id = json.loads(resp4.text)['data']['user_id']
    mp_app_id = json.loads(resp4.text)['data']['mp_app_id']
    headers2 ={
        'User-Agent':f'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.45(0x18002d27) NetType/WIFI Language/zh_CN miniProgram/{mp_app_id}',
        'Referer': f'https://www.ukh5.com/g/12/PaoKu/index.html?beecre_user_id={user_id}'
    }
    #玩游戏
    print('开始玩游戏任务》》》')
    for j in range(3):
        resp5= session.post(f'https://www.ukh5.com/g/12/PaoKu/api.php?a=sumbitscore&openid={user_id}&score=200',headers=headers2)
        result5 = json.loads(resp5.text)
        print(result5)

    if current_date.hour > 23:
        for i in range(3):
            data ={"code":"SCENE-202312221126017708681600711680","provice_name":"浙江省","city_name":"宁波市","area_name":"江北区","address":"浙江省宁波市江北区万达广场","longitude":longitude,"dimension":dimension}
            resp6 = session.post('https://gateway.jmhd8.com/geement.marketinglottery/api/v1/marketinglottery',headers=headers,data=json.dumps(data))
            result6 = json.loads(resp6.text)
            if result6['success'] == True and result6['data']['prizedto']['prize_name']:
                prize =result6['data']['prizedto']['prize_name']
                print(prize)
                if '龙年' in prize:
                    msg = f'账号{a+1}获得{prize}'
                    Push(contents=msg)
                else:
                    print(result6)
###做任务得的次数每天不清空 如果想每天都用掉 就把下面的93行到102行的注释去掉
        # for i in range(7):
        #     data2 ={"code":"SCENE-202312221201352052951600711680","provice_name":"浙江省","city_name":"宁波市","area_name":"江北区","address":"浙江省宁波市江北区万达广场","longitude":longitude,"dimension":dimension}
        #     resp7 = session.post('https://gateway.jmhd8.com/geement.marketinglottery/api/v1/marketinglottery',headers=headers,data=json.dumps(data2))
        #     result7 = json.loads(resp7.text)
        #     if result7['success'] == True and result7['data']['prizedto']['prize_name']:
        #         prize =result7['data']['prizedto']['prize_name']
        #         print(prize)
        #         if '龙年' in prize:
        #             msg = f'账号{a+1}获得{prize}'
        #             Push(contents=msg)
            else:
                print(result7)
