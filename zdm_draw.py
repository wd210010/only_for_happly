#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 7,10 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('值得买每日转盘签到')

import requests, demjson ,re,time,json,os
from datetime import datetime

# 把值得买的cookie放入下面的单引号里面  有几个帐号就弄几个（默认设置了3个 根据自己情况改）
# 青龙变量 zdm_cookie zdm_active_id
zdm_cookie = os.getenv("zdm_cookie").split('&')

zdm_active_id=['ljX8qVlEA7','A6X1veWE2O','OP28eJ7EW7']
Current_date = str(datetime. now(). date())[:7]

for i in range(len(zdm_cookie)):
    for a in range(len(zdm_active_id)):
        projectList = []
        url = f'https://zhiyou.smzdm.com/user/lottery/jsonp_draw?active_id={zdm_active_id[a]}'
        rewardurl= f'https://zhiyou.smzdm.com/user/lottery/jsonp_get_active_info?active_id={zdm_active_id[a]}'
        infourl = 'https://zhiyou.smzdm.com/user/'
        headers = {
            'Host': 'zhiyou.smzdm.com',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Cookie': zdm_cookie[i],
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/smzdm 10.4.6 rv:130.1 (iPhone 13; iOS 15.6; zh_CN)/iphone_smzdmapp/10.4.6/wkwebview/jsbv_1.0.0',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Referer': 'https://m.smzdm.com/',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        response = requests.post(url=url, headers=headers).text
        response_info = requests.get(url=infourl, headers=headers).text
        response_reward = requests.get(url=rewardurl, headers=headers)
        result_reward = json.loads(response_reward.text)
        name = str(re.findall('<a href="https://zhiyou.smzdm.com/user"> (.*?) </a>', str(response_info), re.S)).replace('[','').replace(']','').replace('\'','')
        level = str(re.findall('<img src="https://res.smzdm.com/h5/h5_user/dist/assets/level/(.*?).png\?v=1">', str(response_info), re.S)).replace('[','').replace(']','').replace('\'','')
        gold = str(re.findall('<div class="assets-part assets-gold">\n                    (.*?)</span>', str(response_info), re.S)).replace('[','').replace(']','').replace('\'’','').replace('<span class="assets-part-element assets-num">','').replace('\'','')
        silver = str(re.findall('<div class="assets-part assets-prestige">\n                    (.*?)</span>', str(response_info), re.S)).replace('[','').replace(']','').replace('\'’','').replace('<span class="assets-part-element assets-num">','').replace('\'','')
        data = demjson.decode(str(response), encoding='utf-8')
        a = []
        for j in range(1, 12):
            url2 = f'https://zhiyou.m.smzdm.com/user/exp/ajax_log?page={j}'
            headers2 = {
                'Host': 'zhiyou.m.smzdm.com',
                'Accept': 'application/json, text/plain, */*',
                'Connection': 'keep-alive',
                'Cookie': zdm_cookie[i],
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/smzdm 10.4.40 rv:137.6 (iPhone 13; iOS 15.6; zh_CN)/iphone_smzdmapp/10.4.40/wkwebview/jsbv_1.0.0',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Referer': 'https://zhiyou.m.smzdm.com/user/exp/',
                'Accept-Encoding': 'gzip, deflate, br'
            }
            resp = requests.get(url=url2, headers=headers2)
            result = json.loads(resp.text)['data']['rows']

            for k in range(len(result)):
                a_date = str(result[k]['creation_date'])[:7]

                if a_date == Current_date:
                    b = result[k]['add_exp']
                    a.append(b)
        print('帐号' + str(i + 1) + ' VIP' + level + ' ' + name + ' ' + data[
            'error_msg'] + '  剩余碎银 ' + silver + '  剩余金币 ' + gold + '  本月获得经验：' + str(sum(a)))
