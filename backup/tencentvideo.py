#!/usr/bin/python3
# -- coding: utf-8 --
#@Author : github@raindrop https://github.com/raindrop-hb/tencent-video
# @Time : 2023/3/31 10:23
# -------------------------------
# cron "30 0,1,2 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('腾讯视频签到');

import requests
import json
import time,os


#抓取腾讯视频会员app（不是网页）界面的cookie里面的项目 设置环境变量 只能完成部分任务 还有不是所有帐号都能签到成功因为有的帐号会触发滑块认证或者短信验证 设置定时早上6点前比较好
# export tencent_vdevice_qimei36=''
# export tencent_vqq_appid=''
# export tencent_vqq_openid=''
# export tencent_vqq_access_token=''
# export tencent_main_login='qq' 默认就是qq两个字母 不要瞎改成QQ号

tencent_vdevice_qimei36 = os.getenv("tencent_vdevice_qimei36")
tencent_vqq_appid = os.getenv("tencent_vqq_appid")
tencent_vqq_openid = os.getenv("tencent_vqq_openid")
tencent_vqq_access_token = os.getenv("tencent_vqq_access_token")
tencent_main_login = os.getenv("tencent_main_login")


def ten_video():
    cookie='vdevice_qimei36='+tencent_vdevice_qimei36+';vqq_appid='+tencent_vqq_appid+';vqq_openid='+tencent_vqq_openid+';vqq_access_token='+tencent_vqq_access_token+';main_login='+tencent_main_login
    url_1='https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/CheckIn?rpc_data=%7B%7D'
    headers_1={'user-agent':'Mozilla/5.0 (Linux; Android 11; M2104K10AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046237 Mobile Safari/537.36 QQLiveBrowser/8.7.85.27058',
             'Content-Type':'application/json',
             'referer':'https://film.video.qq.com/x/vip-center/?entry=common&hidetitlebar=1&aid=V0%24%241%3A0%242%3A8%243%3A8.7.85.27058%244%3A3%245%3A%246%3A%247%3A%248%3A4%249%3A%2410%3A&isDarkMode=0',
             'cookie':cookie
             }
    response_1 = requests.get(url_1,headers=headers_1)
    res_1 = json.loads(response_1.text)
    url_2='https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/ProvideAward?rpc_data=%7B%22task_id%22:1%7D'
    headers_2={'user-agent':'Mozilla/5.0 (Linux; Android 11; M2104K10AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046237 Mobile Safari/537.36 QQLiveBrowser/8.7.85.27058',
             'Content-Type':'application/json',
             'referer':'https://film.video.qq.com/x/vip-center/?entry=common&hidetitlebar=1&aid=V0%24%241%3A0%242%3A8%243%3A8.7.85.27058%244%3A3%245%3A%246%3A%247%3A%248%3A4%249%3A%2410%3A&isDarkMode=0',
             'cookie':cookie
             }
    response_2 = requests.get(url_2,headers=headers_2)
    res_2 = json.loads(response_2.text)
    time_1 = int(time.time())
    time_2 = time.localtime(time_1)
    now = time.strftime("%Y-%m-%d %H:%M:%S", time_2)
    log = "腾讯视频会员签到执行任务\n----------raindrop----------\n" + now
    try:
        log = log + "\n签到获得积分:" + str(res_1['check_in_score'])
    except:
        log=log+"\n腾讯视频签到异常，返回内容："+str(res_1)
        print(res_1)
    try:
        log = log + "\n观看获得积分:" + str(res_2['check_in_score'])
    except:
        log=log+"\n腾讯视频领取观看积分异常,返回内容："+str(res_2)
        print(res_2)
    url='https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/ReadTaskList?rpc_data=%7B%22business_id%22:%221%22,%22platform%22:3%7D'
    headers={'user-agent':'Mozilla/5.0 (Linux; Android 11; M2104K10AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046237 Mobile Safari/537.36 QQLiveBrowser/8.7.85.27058',
             'Content-Type':'application/json',
             'referer':'https://film.video.qq.com/x/vip-center/?entry=common&hidetitlebar=1&aid=V0%24%241%3A0%242%3A8%243%3A8.7.85.27058%244%3A3%245%3A%246%3A%247%3A%248%3A4%249%3A%2410%3A&isDarkMode=0',
             'cookie':cookie
             }
    response = requests.get(url,headers=headers)
    res = json.loads(response.text)
    try:
        lis=res["task_list"]
        log = log + '\n--------任务状态----------'
        for i in lis:
            log=log+'\ntask_title:'+i["task_maintitle"]+'\nsubtitle:'+i["task_subtitle"]+'\ntask_button_desc:'+i["task_button_desc"]
    except:
        log = log + "获取状态异常，可能是cookie失效"
        print(res)
    print(log)
    

def main():
    ten_video()


def main_handler(event, context):
    return main()


if __name__ == '__main__':
    main()
